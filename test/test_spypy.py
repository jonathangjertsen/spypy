import json
import os
from types import TracebackType

import pytest

import spypy
from .functions_for_test import trivial_function, function_with_args, function_that_raises_exception


def test_no_shadowing_of_builtins():
    builtin_set = set(dir(__builtins__))
    assert builtin_set & set(spypy.Snapshot._fields) == set()
    assert builtin_set & set(spypy._FastSnapshot._fields) == set()
    assert builtin_set & set(dir(spypy)) == { "__doc__" }


def test_ensure_serializable_simple():
    assert spypy.ensure_serializable({"a": 2, "b": 3}) == {"a": 2, "b": 3}


def test_ensure_serializable_with_nonserializable_fill_with_none(non_serializable_object):
    in_dict = {"a": 2, "b": non_serializable_object}
    out_dict = {"a": 2, "b": None}
    assert (spypy.ensure_serializable(in_dict) == out_dict)


def test_ensure_serializable_with_nonserializable_fill_with_string(non_serializable_object):
    fill_str = "abracadabra"
    in_dict = {"a": 2, "b": non_serializable_object}
    out_dict = {"a": 2, "b": fill_str}
    assert (spypy.ensure_serializable(in_dict, fill_str) == out_dict)


def test_ensure_serializable_with_nonserializable_fill_with_function(non_serializable_object):
    def fill_func(obj):
        return type(obj).__name__
    in_dict = {"a": 2, "b": non_serializable_object}
    out_dict = {"a": 2, "b": fill_func(non_serializable_object)}
    assert (spypy.ensure_serializable(in_dict, fill_func) == out_dict)


def test_tracer_initial_results_of_public_api_calls(tracer):
    assert (
        tracer.uncaught_exception,
        tracer.trace_completed,
        tracer.snapshots(),
        tracer.json(),
        tracer.csv().strip(),
    ) == (
        None,
        False,
        [],
        "[]",
        ",".join(spypy.Snapshot._fields),
    )


def test_trivial_function_runs():
    assert trivial_function() == 3


def test_function_with_arg_runs():
    assert function_with_args(1, 2, z=3) == 6


def test_function_that_raises_exception_raises_exception():
    with pytest.raises(ValueError):
        function_that_raises_exception()


def test_trival_function_returns_same_when_traced(tracer):
    assert trivial_function() == tracer.trace(trivial_function)


def test_function_with_arg_returns_same_when_traced(tracer):
    assert function_with_args(1, 2, z=3) == tracer.trace(function_with_args, 1, 2, z=3)


def test_tracer_trivial_function_no_uncaught_exception(tracer):
    tracer.trace(trivial_function)
    assert tracer.uncaught_exception is None


def test_function_that_raises_exception_returns_none_when_traced(tracer):
    assert tracer.trace(function_that_raises_exception) is None


def test_function_that_raises_exception_populates_uncaught_exception(tracer):
    tracer.trace(function_that_raises_exception)
    assert tracer.uncaught_exception is not None


def test_tracer_trivial_function_reproducibility(tracer):
    """
    Test with a "trivial" function
    """
    tracer.trace(trivial_function)

    first_call = tracer.snapshots()
    second_call = tracer.snapshots()

    assert first_call == second_call
    assert first_call is not second_call

def test_tracer_trivial_function_globals(tracer):
    tracer.trace(trivial_function)
    assert [
        snapshot.globals_
        for snapshot in tracer.snapshots()
    ] == [None] * trivial_function.length


def test_tracer_trivial_function_locals(tracer):
    tracer.trace(trivial_function)
    assert [
        snapshot.locals_
        for snapshot in tracer.snapshots()
    ] == [
        {},
        {"a": 1},
        {"a": 1, "b": 2},
        {"a": 1, "b": 2, "c": 3},
        {"a": 1, "c": 3},
    ]


def test_tracer_trivial_function_line_numbers(tracer):
    tracer.trace(trivial_function)
    assert [
        snapshot.line_number
        for snapshot in tracer.snapshots()
    ] == [trivial_function.start + i + 1 for i in range(trivial_function.length)]


def test_tracer_trivial_function_filename(tracer):
    tracer.trace(trivial_function)
    assert all(
        snapshot.filename.endswith("functions_for_test.py")
        for snapshot in tracer.snapshots()
    )


def test_tracer_trivial_function_line_content(tracer):
    with open(os.path.join(os.path.dirname(__file__), "functions_for_test.py")) as file:
        lines = [line.rstrip() for line in file.readlines()]
    relevant_lines = lines[trivial_function.start:trivial_function.start+trivial_function.length]

    tracer.trace(trivial_function)

    assert [snapshot.line_content for snapshot in tracer.snapshots()] == relevant_lines


def test_tracer_trivial_function_json(tracer):
    tracer.trace(trivial_function)

    jsonstr = tracer.json()
    data = json.loads(jsonstr)

    assert [spypy.Snapshot(**entry) for entry in data] == tracer.snapshots()


def test_tracer_trivial_function_csv(tracer):
    tracer.trace(trivial_function)

    header_n_lines = 1
    trailing_newline_n_lines = 1

    csvstr = tracer.csv()
    assert len(csvstr.split("\n")) == header_n_lines + trivial_function.length + trailing_newline_n_lines


def test_tracer_trivial_function_save_csv(tracer):
    tracer.trace(trivial_function)

    try:
        tracer.save_csv("csv.csv")
        with open("csv.csv") as file:
            file_ignore_newlines = file.read().replace("\r\n", "\n")
        csv_ignore_newlines = tracer.csv().replace("\r\n", "\n")
        assert file_ignore_newlines == csv_ignore_newlines
    finally:
        os.remove("csv.csv")


def test_tracer_exception(tracer):
    def bad_function_a():
        raise ValueError("Oops!")
    def bad_function_b():
        return bad_function_a()

    tracer.trace(bad_function_b)

    assert tracer.uncaught_exception is not None
    assert len(tracer.uncaught_exception) == 3
    assert tracer.uncaught_exception[0] == ValueError
    assert isinstance(tracer.uncaught_exception[1], ValueError)
    assert isinstance(tracer.uncaught_exception[2], TracebackType)


def test_tracer_context_manager(tracer):
    def a():
        v = 1
        b = 2
        raise ValueError("Oops")

    with tracer:
        a()

    assert len(tracer.snapshots()) == 3
    assert tracer.uncaught_exception


def test_tracer_context_manager_as(tracer):
    def a():
        v = 1
        b = 2
        raise ValueError("Oops")

    with tracer as tracer_:
        assert tracer_ is tracer
        a()

    assert len(tracer.snapshots()) == 3
    assert tracer.uncaught_exception


def test_tracer_context_manager_twice(tracer):
    def a():
        v = 1
        b = 2

    with tracer:
        a()
        a()

    assert len(tracer.snapshots()) == 4
    assert not tracer.uncaught_exception
