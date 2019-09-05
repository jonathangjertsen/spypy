# spypy
Spy on your Python code by snapshotting the application state for each line of code

Example file: 

```
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
```

Output:

```
>python example.py
[
  {
    "event": "call",
    "arg": null,
    "frame": {
      "lineno": 6,
      "code": {
        "filename": "example.py"
      },
      "locals": {}
    }
  },
  {
    "event": "line",
    "arg": null,
    "frame": {
      "lineno": 7,
      "code": {
        "filename": "example.py"
      },
      "locals": {}
    }
  },
  {
    "event": "call",
    "arg": null,
    "frame": {
      "lineno": 3,
      "code": {
        "filename": "example.py"
      },
      "locals": {
        "x": 2
      }
    }
  },
  {
    "event": "line",
    "arg": null,
    "frame": {
      "lineno": 4,
      "code": {
        "filename": "example.py"
      },
      "locals": {
        "x": 2
      }
    }
  },
  {
    "event": "return",
    "arg": 4,
    "frame": {
      "lineno": 4,
      "code": {
        "filename": "example.py"
      },
      "locals": {
        "x": 2
      }
    }
  },
  {
    "event": "line",
    "arg": null,
    "frame": {
      "lineno": 8,
      "code": {
        "filename": "example.py"
      },
      "locals": {
        "a": 4
      }
    }
  },
  {
    "event": "call",
    "arg": null,
    "frame": {
      "lineno": 3,
      "code": {
        "filename": "example.py"
      },
      "locals": {
        "x": 4
      }
    }
  },
  {
    "event": "line",
    "arg": null,
    "frame": {
      "lineno": 4,
      "code": {
        "filename": "example.py"
      },
      "locals": {
        "x": 4
      }
    }
  },
  {
    "event": "return",
    "arg": 16,
    "frame": {
      "lineno": 4,
      "code": {
        "filename": "example.py"
      },
      "locals": {
        "x": 4
      }
    }
  },
  {
    "event": "return",
    "arg": 16,
    "frame": {
      "lineno": 8,
      "code": {
        "filename": "example.py"
      },
      "locals": {
        "a": 4
      }
    }
  }
]
```
