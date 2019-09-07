import json

from spypy import Tracer

def square(x):
    return x * x

def some_function():
    a = 2
    result = json.loads("[]")
    i = 5
    while (i > 0):
        a = square(a + 1)
        result.append(a)
        i -= 1
    return result

if __name__ == "__main__":
    tracer = Tracer(non_serializable_fill=repr)
    tracer.trace(some_function)
    print(tracer.csv())
