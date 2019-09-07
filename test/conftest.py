import pytest

from spypy import Tracer

@pytest.fixture()
def tracer():
    return Tracer()


@pytest.fixture()
def non_serializable_object():
    class NonSerializable(object):
        pass
    return NonSerializable()