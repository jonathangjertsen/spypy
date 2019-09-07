import os

import pytest

from spypy import Tracer, make_linetrace_csv
from .functions_for_test import trivial_function, nontrivial_function
from .files_test.b import func_b

@pytest.fixture()
def tracer():
    return Tracer()


def test_make_tracer():
    tracer = Tracer()
    assert tracer is not None


def test_run_tracer(tracer):
    """
    Test with a "trivial" function
    """
    tracer.trace(trivial_function)
    results = tracer.results()

    assert len(results) == 6

    assert results[0]["event"] == "call"
    assert all(result["event"] == "line" for result in results[1:-1])
    assert results[-1]["event"] == "return"

    assert all(result["arg"] is None for result in results[:-1])
    assert results[-1]["arg"] == 3


def test_save_json(tracer):
    json_filename = "dummy_json.json"

    try:
        tracer.trace(nontrivial_function)
        tracer.save_json(json_filename)
    finally:
        os.remove(json_filename)


def test_list_filenames(tracer):
    tracer.trace(func_b)

    files = tracer.filenames()
    assert len(files) == 2


def test_linetrace(tracer):
    csv_filename = "dummy_csv.csv"

    tracer.trace(func_b)
    lines = tracer.linetrace()

    try:
        make_linetrace_csv(lines, csv_filename)
    finally:
        os.remove(csv_filename)
