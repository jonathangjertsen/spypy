from spypy import Tracer, make_linetrace_csv

def square(x):
    return x * x

def some_function():
    a = 1
    result = []
    i = 5
    while (i > 0):
        a = square(a + 1)
        result.append(a)
        i -= 1
    return result

if __name__ == "__main__":
    tracer = Tracer(non_serializable_fill=repr)
    tracer.trace(some_function)
    make_linetrace_csv(tracer.linetrace(), "example.csv")
    with open("example.csv") as example:
        print(example.read())
