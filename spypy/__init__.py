from csv import DictWriter
from copy import deepcopy
import json
import sys
from collections import OrderedDict
from typing import Any, Union, Callable, List

Primitive = Union[int, float, str, bool, None]

class RequiredFieldMissing(KeyError):
    pass

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
    return deepcopy(output_dict)

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
        if "filename" in self.fields:
            result["filename"] = self.frame.f_code.co_filename
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

def format_fields(in_dict, indent=0):
    lines = []
    for key, value in in_dict.items():
        lines.append("-" + "-" * indent + "> " +  key)
        if isinstance(value, dict):
            lines.extend(format_fields(value, indent + 1))
    if indent == 0:
        return "\n".join(lines)
    else:
        return lines

class ExecutedLine(object):
    def __init__(self, file, line_number, line_content, locals=None, globals=None):
        self.file = file
        self.line_number = line_number
        self.line_content = line_content
        self.locals = locals

    @classmethod
    def fields(cls):
        return ("file", "line_number", "line_content", "locals")

    def to_dict(self):
        return OrderedDict([
            (attr, getattr(self, attr))
            for attr in type(self).fields()
        ])

def make_linetrace_csv(list_of_executed_lines, filename):
    with open(filename, "w", newline="") as file:
        writer = DictWriter(file, fieldnames=ExecutedLine.fields())
        writer.writeheader()
        for line in list_of_executed_lines:
            writer.writerow(line.to_dict())

class Tracer(object):
    @classmethod
    def default_fields(cls):
        return {
            "frame": {
                "code": {
                    "filename": "",
                },
                "lineno": "",
                "locals": "",
            },
            "event": "",
            "arg": "",
            "filename": "",
        }

    def __init__(self, fields=None, non_serializable_fill=None):
        self._orig_trace = None
        self._results = []
        if fields is None:
            fields = type(self).default_fields()
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

    def check_field_was_captured(self, path):
        fields = self.fields
        for field in path:
            if field not in fields:
                raise RequiredFieldMissing(
                    "{} was not captured during trace. Fields: {}".format(
                        "->".join(path),
                        format_fields(self.fields)
                    )
                )
            fields = fields[field]

    def filenames(self):
        self.check_field_was_captured(("filename", ))
        return set(result["filename"] for result in self._results)

    def _file_contents(self):
        filenames = self.filenames()
        file_contents = {}
        for filename in filenames:
            with open(filename) as file:
                file_contents[filename] = file.readlines()
        return file_contents

    def linetrace(self):
        self.check_field_was_captured(("filename",))
        self.check_field_was_captured(("frame", "lineno"))
        self.check_field_was_captured(("event",))

        file_contents = self._file_contents()
        lines = []
        for result in self._results:
            if result["event"] == "line":
                file = result["filename"]
                line_number = result["frame"]["lineno"]
                lines_for_file = file_contents[file]
                line_content = lines_for_file[line_number - 1].rstrip()

                try:
                    locals = result["frame"]["locals"]
                except KeyError:
                    locals = None

                try:
                    globals = result["frame"]["globals"]
                except KeyError:
                    globals = None

                lines.append(ExecutedLine(
                    file=file,
                    line_number=line_number,
                    line_content=line_content,
                    locals=locals,
                    globals=globals,
                ))
        return lines