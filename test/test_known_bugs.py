import pytest

@pytest.mark.skip
def test_bug_tracer_context_manager_naked_code(tracer):
    with tracer:
        v = 1
        b = 2
        raise ValueError("Oops")

    assert len(tracer.snapshots()) == 3
    assert tracer.uncaught_exception
