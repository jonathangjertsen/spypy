"""
A library which lets you spy on your Python code by taking a
snapshot of the application state during every line that gets executed.
"""

### IMPORTS

from collections import namedtuple, OrderedDict
from contextlib import contextmanager
from copy import deepcopy
from csv import DictWriter
import io
import json
import sys
from types import FrameType, TracebackType
from typing import Any, Callable, Dict, List, Optional, Union, Tuple, Set

### TYPES

SnapshotData = Dict[str, Any]
Primitive = Union[int, float, str, bool, None]
TraceFunc = Callable[[FrameType, str, Any], 'TraceFunc']

### CONSTANTS

# Setting this to True currently breaks when running pytest --cov
# This workaround prevents it from breaking, at the cost of pytest thinking some
# lines have not been ran (since its own trace function is not applied there)
COOPERATION_WITH_OTHER_USERS_OF_SYS_SETTRACE_IS_POSSIBLE = False

IGNORED_FILES = {
    "<frozen importlib._bootstrap>",
    __file__,
}

### DATA CONTAINERS

Snapshot = namedtuple("Snapshot", "filename line_number line_content globals_ locals_")
Snapshot.__doc__ = """Snapshot of the application when the given line was executed."""

_FastSnapshot = namedtuple("_FastSnapshot", "filename line_number event globals_ locals_")
_FastSnapshot.__doc__ = """Snapshot of the application when the given line was executed.

This version is created during execution, and is faster to create than a Snapshot because it
does not need to access the file system.
"""

### CLASSES THAT DO THINGS

class Tracer(object):

    ### PUBLIC API FOR TRACING

    def __init__(self, capture_locals=True, capture_globals=False, non_serializable_fill=repr):
        """Initializes the Tracer object with a configuration and an empty list of snapshots."""
        # A list of all the snapshots that were taken during execution.
        self._snapshots = []

        # Remembers the original tracing function that was used before the most recent call to self._start()
        # Will be reapplied as the tracing function on a call to self._stop().
        self._orig_trace = None

        # A boolean, whether to capture the local variables in each snapshot.
        # May be set to False for improved performance (the global variables need to be serialized for every snapshot).
        # Set to True by default since the history of local variables often gives insight into any bugs that occur during execution.
        self.capture_locals = capture_locals

        # A boolean, whether to capture the _globals in each snapshot.
        # May be set to False for improved performance (the global variables need to be serialized for every snapshot).
        # Set to False by default because they rarely change and cause a lot of noise to be present in the output.
        self.capture_globals = capture_globals

        # Many values are not serializable. In this case, some action must be performed to represent the value.
        # non_serializable_fill may either be:
        # - A value, in which case each non-serializable value is replaced with the fill value
        # - A function which takes one argument and is applied to the value. The value is replaced with the return value of the fill function.
        # Set to the `repr` function by default.
        self._non_serializable_fill = non_serializable_fill

        # If an exception was caught during a call to `self.trace()` or `with self`, this value will be populated with the
        # exception data.
        # The value will be the tuple (exc_type, exc_value, exc_traceback).
        self.uncaught_exception = None

        # Whether a trace has been completed.
        self.trace_completed = False

    def reset_history(self):
        """
        Makes the Tracer object appear as if it has never performed a trace.
        """
        self._snapshots = []
        self.uncaught_exception = None
        self.trace_completed = False

    def trace(self, func: Callable, *args, **kwargs):
        """
        Traces a function call (with any arguments).

        Any uncaught exceptions will be stored in self.uncaught_exception
        """
        self._start()
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as exc:
            self.uncaught_exception = sys.exc_info()
        finally:
            self._stop()

    def __enter__(self) -> 'Tracer':
        """Makes the tracer available as a context manager"""
        self._start()
        return self

    def __exit__(self, exc_type: type, exc_value: BaseException, traceback: TracebackType) -> bool:
        """Executed upon exiting the context manager."""
        # Make a note of the exception, if any
        if exc_type is not None:
            self.uncaught_exception = (exc_type, exc_value, traceback)

        # Finish up
        self._stop()

        # Prevent any exceptions from propagating into the external context by returning True
        return True

    # PUBLIC API FOR OPERATING ON TRACE RESULTS

    def snapshots(self) -> List[Snapshot]:
        file_contents = self._file_contents()

        return [
            Snapshot(
                line_number=snapshot.line_number,
                filename=snapshot.filename,
                locals_=snapshot.locals_,
                globals_=snapshot.globals_,
                line_content=file_contents[snapshot.filename][snapshot.line_number - 1].rstrip()
            )
            for snapshot in self._snapshots
            if snapshot.event == "line"
        ]

    def json(self, indent=2) -> str:
        return json.dumps([
            dict(snapshot._asdict())
            for snapshot in self.snapshots()
        ], indent=indent)

    def csv(self) -> str:
        return make_linetrace_csv(self.snapshots())

    def save_csv(self, filename: str):
        make_linetrace_csv(self.snapshots(), filename)

    # HELPERS

    def _start(self, reset_history: bool=True):
        """
        Starts tracing by registering a new trace function.
        This will overwrite any previous trace function, but calling _stop() will re-apply it.

        If reset_history is True, this will erase any memory of previous traces.
        If reset_history is False, snapshots from this trace will be appended to snapshots from previous traces.
        """
        if reset_history:
            self.reset_history()

        self._orig_trace = sys.gettrace()
        sys.settrace(self._trace_func)

    def _stop(self):
        """
        Stops tracing by unregistering the trace function.
        """
        sys.settrace(self._orig_trace)
        self.trace_completed = True

    def _trace_func(self, frame: FrameType, event: str, arg: Any) -> TraceFunc:
        """Callback for sys.settrace

        https://docs.python.org/3.5/library/sys.html#sys.settrace
        """
        if frame.f_code.co_filename not in IGNORED_FILES:
            self._snapshots.append(_FastSnapshot(
                filename=frame.f_code.co_filename,
                line_number=frame.f_lineno,
                event=event,
                globals_=ensure_serializable(
                    frame.f_globals, self._non_serializable_fill
                ) if self.capture_globals else None,
                locals_=ensure_serializable(
                    frame.f_locals, self._non_serializable_fill
                ) if self.capture_locals else None,
            ))

        if self._orig_trace is not None and COOPERATION_WITH_OTHER_USERS_OF_SYS_SETTRACE_IS_POSSIBLE:
            try:
                sys.settrace(None)
                self._orig_trace(frame, event, arg)
            finally:
                sys.settrace(self._trace_func)

        return self._trace_func

    def _filenames(self) -> Set[str]:
        return set(snapshot.filename for snapshot in self._snapshots)

    def _file_contents(self):
        filenames = self._filenames()
        file_contents = {}
        for filename in filenames:
            with open(filename) as file:
                file_contents[filename] = file.readlines()
        return file_contents

### STANDALONE FUNCTIONS

def ensure_serializable(input_dict: dict, non_serializable_fill: Union[Callable[[Any], Primitive], Primitive]=None) -> dict:
    output_dict = {}
    for key, value in input_dict.items():
        try:
            dump = json.dumps(value)
            output_dict[key] = json.loads(dump)
        except:
            if callable(non_serializable_fill):
                output_dict[key] = non_serializable_fill(value)
            else:
                output_dict[key] = non_serializable_fill
    return output_dict

def make_linetrace_csv(snapshots, filename: Optional[str]=None) -> Optional[str]:
    if filename:
        with open(filename, "w", newline="") as file:
            _write_linetrace_csv(snapshots, file)
            return None
    else:
        output = io.StringIO()
        _write_linetrace_csv(snapshots, output)
        return output.getvalue()

def _write_linetrace_csv(snapshots, handle):
    writer = DictWriter(handle, fieldnames=Snapshot._fields)
    writer.writeheader()
    for line in snapshots:
        writer.writerow(line._asdict())