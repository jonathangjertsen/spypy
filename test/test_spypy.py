import os

from spypy import Tracer
from .functions_for_test import trivial_function, nontrivial_function

def test_make_tracer():
    tracer = Tracer()
    assert tracer is not None

def test_run_tracer():
    """
    Test with a "trivial" function
    """
    tracer = Tracer({
        "frame": {
            "code": {
                "filename": "",
                "lineno": "",
            }
        },
        "event": "",
        "arg": "",
    })
    tracer.trace(trivial_function)
    results = tracer.results()

    assert len(results) == 6

    assert results[0]["event"] == "call"
    assert all(result["event"] == "line" for result in results[1:-1])
    assert results[-1]["event"] == "return"

    assert all(result["arg"] is None for result in results[:-1])
    assert results[-1]["arg"] == 3

def test_save_json():
    json_filename = "dummy_json.json"

    try:
        tracer = Tracer({
            "frame": {
                "code": {
                    "filename": "",
                },
                "lineno": "",
                "locals": "",
            },
            "event": "",
            "arg": "",
        })
        tracer.trace(nontrivial_function)
        tracer.save_json(json_filename)
    finally:
        os.remove(json_filename)
