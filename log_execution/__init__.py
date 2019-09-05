import json
import sys
from typing import Any, Union, Callable

Primitive = Union[int, float, str, bool, None]

def ensure_serializable(input_dict: dict, non_serializable_fill: Union[Callable[[Any], Primitive], Primitive]=None) -> dict:
    output_dict = {}
    for key, value in input_dict.items():
        try:
            json.dumps(value)
        except:
            if callable(non_serializable_fill):
                output_dict[key] = non_serializable_fill(value)
            else:
                output_dict[key] = non_serializable_fill
        else:
            output_dict[key] = value
    return output_dict

class TracedEvent(object):
    __slots__ = ["frame", "event", "arg", "fields"]
    def __init__(self, frame, event, arg, fields=None):
        self.frame = frame
        self.event = event
        self.arg = arg
        if fields is None:
            self.fields = {}
        else:
            self.fields = fields

    def __str__(self):
        return ("TracedEvent("
            "line={}, file={}, event={}, arg={}"
            ")").format(
            self.frame.f_lineno,
            self.frame.f_code.co_filename,
            self.event,
            self.arg
        )

    def __repr__(self):
        return str(self)

    def to_dict(self, non_serializable_fill):
        result = {}
        if "event" in self.fields:
            result["event"] = self.event
        if "arg" in self.fields:
            result["arg"] = self.arg
        if "frame" in self.fields:
            frame = {}
            result["frame"] = frame
            frame_fields = self.fields["frame"]
            if "id" in frame_fields:
                frame["id"] = id(self.frame.f_back)
            if "lineno" in frame_fields:
                frame["lineno"] = self.frame.f_lineno
            if "globals" in frame_fields:
                frame["globals"] = ensure_serializable(self.frame.f_globals, non_serializable_fill)
            if "locals" in frame_fields:
                frame["locals"] = ensure_serializable(self.frame.f_locals, non_serializable_fill)
            if "code" in frame_fields:
                code = {}
                frame["code"] = code
                code_fields = frame_fields["code"]
                if "argcount" in code_fields:
                    code["argcount"] = self.frame.f_code.co_argcount
                if "varnames" in code_fields:
                    code["varnames"] = self.frame.f_code.co_varnames
                if "filename" in code_fields:
                    code["filename"] = self.frame.f_code.co_filename
        return result

class Tracer(object):
    def __init__(self, fields=None, non_serializable_fill=None):
        self._orig_trace = None
        self._results = []
        self.fields = fields
        self.non_serializable_fill = non_serializable_fill

    def start(self):
        self._orig_trace = sys.gettrace()
        sys.settrace(self.trace_func)

    def stop(self):
        # Unregister the tracer
        sys.settrace(self._orig_trace)

        # The part of the code that unregistered the tracer will
        # have gotten included in the trace, remove it here.
        remove_from_index = -1
        for event_no, result in enumerate(self._results):
            try:
                if result['frame']['code']['filename'] == __file__:
                    remove_from_index = event_no
                    break
            except KeyError:
                pass
        self._results = self._results[:remove_from_index]

    def trace(self, func, *args, **kwargs):
        try:
            self.start()
            func(*args, **kwargs)
        finally:
            self.stop()

    def trace_func(self, frame, event, arg):
        """Callback for sys.settrace

        https://docs.python.org/3.5/library/sys.html#sys.settrace
        """
        if frame.f_code.co_filename == "<frozen importlib._bootstrap>":
            return self.trace_func
        self._results.append(TracedEvent(frame, event, arg, self.fields).to_dict(self.non_serializable_fill))
        return self.trace_func

    def results(self):
        return self._results

    def json(self):
        return json.dumps([ensure_serializable(result) for result in self._results], indent=2)

    def save_json(self, filename):
        with open(filename, "w") as json_file:
            json_file.write(self.json())
