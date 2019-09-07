# spypy
Spy on your Python code by snapshotting the application state for each line of code

Example file: 

```
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
```

Output:

```
>python example.py
file,line_number,line_content,locals
example.py,7,    a = 1,{}
example.py,8,    result = [],{'a': 1}
example.py,9,    i = 5,"{'a': 1, 'result': []}"
example.py,10,    while (i > 0):,"{'i': 5, 'a': 1, 'result': []}"
example.py,11,        a = square(a + 1),"{'i': 5, 'a': 1, 'result': []}"
example.py,4,    return x * x,{'x': 2}
example.py,12,        result.append(a),"{'i': 5, 'a': 4, 'result': []}"
example.py,13,        i -= 1,"{'i': 5, 'a': 4, 'result': [4]}"
example.py,10,    while (i > 0):,"{'i': 4, 'a': 4, 'result': [4]}"
example.py,11,        a = square(a + 1),"{'i': 4, 'a': 4, 'result': [4]}"
example.py,4,    return x * x,{'x': 5}
example.py,12,        result.append(a),"{'i': 4, 'a': 25, 'result': [4]}"
example.py,13,        i -= 1,"{'i': 4, 'a': 25, 'result': [4, 25]}"
example.py,10,    while (i > 0):,"{'i': 3, 'a': 25, 'result': [4, 25]}"
example.py,11,        a = square(a + 1),"{'i': 3, 'a': 25, 'result': [4, 25]}"
example.py,4,    return x * x,{'x': 26}
example.py,12,        result.append(a),"{'i': 3, 'a': 676, 'result': [4, 25]}"
example.py,13,        i -= 1,"{'i': 3, 'a': 676, 'result': [4, 25, 676]}"
example.py,10,    while (i > 0):,"{'i': 2, 'a': 676, 'result': [4, 25, 676]}"
example.py,11,        a = square(a + 1),"{'i': 2, 'a': 676, 'result': [4, 25, 676]}"
example.py,4,    return x * x,{'x': 677}
example.py,12,        result.append(a),"{'i': 2, 'a': 458329, 'result': [4, 25, 676]}"
example.py,13,        i -= 1,"{'i': 2, 'a': 458329, 'result': [4, 25, 676, 458329]}"
example.py,10,    while (i > 0):,"{'i': 1, 'a': 458329, 'result': [4, 25, 676, 458329]}"
example.py,11,        a = square(a + 1),"{'i': 1, 'a': 458329, 'result': [4, 25, 676, 458329]}"
example.py,4,    return x * x,{'x': 458330}
example.py,12,        result.append(a),"{'i': 1, 'a': 210066388900, 'result': [4, 25, 676, 458329]}"
example.py,13,        i -= 1,"{'i': 1, 'a': 210066388900, 'result': [4, 25, 676, 458329, 210066388900]}"
example.py,10,    while (i > 0):,"{'i': 0, 'a': 210066388900, 'result': [4, 25, 676, 458329, 210066388900]}"
example.py,14,    return result,"{'i': 0, 'a': 210066388900, 'result': [4, 25, 676, 458329, 210066388900]}"
```
