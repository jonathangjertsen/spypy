import json
import os

import pytest

from spypy import Tracer, Snapshot
from .functions_for_test import trivial_function

@pytest.fixture()
def tracer():
    return Tracer()


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
        ",".join(Snapshot._fields),
    )


def test_tracer_trivial_function_reproducibility(tracer):
    """
    Test with a "trivial" function
    """
    tracer.trace(trivial_function)

    assert tracer.snapshots() == tracer.snapshots()
    assert tracer.snapshots() is not tracer.snapshots()

def test_tracer_trivial_function_globals(tracer):
    tracer.trace(trivial_function)
    assert [
        snapshot.globals
        for snapshot in tracer.snapshots()
    ] == [None] * trivial_function.length

def test_tracer_trivial_function_locals(tracer):
    tracer.trace(trivial_function)
    assert [
        snapshot.locals
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

    assert [Snapshot(**entry) for entry in data] == tracer.snapshots()


def test_tracer_trivial_function_csv(tracer):
    tracer.trace(trivial_function)

    header_n_lines = 1
    trailing_newline_n_lines = 1

    csvstr = tracer.csv()
    assert len(csvstr.split("\n")) == header_n_lines + trivial_function.length + trailing_newline_n_lines

