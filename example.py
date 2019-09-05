from spypy import Tracer

def square(x):
    return x * x

def function():
    a = square(2)
    return square(a)


if __name__ == "__main__":
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
    }, non_serializable_fill=repr)
    tracer.trace(function)
    print(tracer.json())
