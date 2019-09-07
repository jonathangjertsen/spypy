# spypy
Spy on your Python code by snapshotting the application state for each line of code

## Install

TODO make available on PyPI

## Usage

```
from spypy import Tracer

if __name__ == "__main__":
    # Run tracer
    tracer = Tracer()
    tracer.trace(your_function, arguments)

    # List-representation
    tracer.snapshots()

    # CSV representatiom
    tracer.csv()

    # JSON representation
    tracer.json()
```

## Example

Example file (nonsensical function just to show some features)

```
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
```

Output:

```
>python example.py
filename,line_number,line_content,globals,locals
example.py,9,    a = 2,,{}
example.py,10,"    result = json.loads(""[]"")",,{'a': 2}
<stdlib>\json\__init__.py,310,"    if not isinstance(s, str):",,"{'s': '[]', 'encoding': None, 'object_pairs_hook': None, 'kw': {}, 'parse_constant': None, 'parse_int': None, 'object_hook': None, 'parse_float': None, 'cls': None}"
<stdlib>\json\__init__.py,313,    if s.startswith(u'\ufeff'):,,"{'s': '[]', 'encoding': None, 'object_pairs_hook': None, 'kw': {}, 'parse_constant': None, 'parse_int': None, 'object_hook': None, 'parse_float': None, 'cls': None}"
<stdlib>\json\__init__.py,316,    if (cls is None and object_hook is None and,,"{'s': '[]', 'encoding': None, 'object_pairs_hook': None, 'kw': {}, 'parse_constant': None, 'parse_int': None, 'object_hook': None, 'parse_float': None, 'cls': None}"
<stdlib>\json\__init__.py,317,            parse_int is None and parse_float is None and,,"{'s': '[]', 'encoding': None, 'object_pairs_hook': None, 'kw': {}, 'parse_constant': None, 'parse_int': None, 'object_hook': None, 'parse_float': None, 'cls': None}"
<stdlib>\json\__init__.py,318,            parse_constant is None and object_pairs_hook is None and not kw):,,"{'s': '[]', 'encoding': None, 'object_pairs_hook': None, 'kw': {}, 'parse_constant': None, 'parse_int': None, 'object_hook': None, 'parse_float': None, 'cls': None}"
<stdlib>\json\__init__.py,319,        return _default_decoder.decode(s),,"{'s': '[]', 'encoding': None, 'object_pairs_hook': None, 'kw': {}, 'parse_constant': None, 'parse_int': None, 'object_hook': None, 'parse_float': None, 'cls': None}"
<stdlib>\json\decoder.py,339,"        obj, end = self.raw_decode(s, idx=_w(s, 0).end())",,"{'_w': '<built-in method match of _sre.SRE_Pattern object at 0x0000014038FBB1B0>', 'self': '<json.decoder.JSONDecoder object at 0x0000014038FA9BE0>', 's': '[]'}"
<stdlib>\json\decoder.py,354,        try:,,"{'s': '[]', 'self': '<json.decoder.JSONDecoder object at 0x0000014038FA9BE0>', 'idx': 0}"
<stdlib>\json\decoder.py,355,"            obj, end = self.scan_once(s, idx)",,"{'s': '[]', 'self': '<json.decoder.JSONDecoder object at 0x0000014038FA9BE0>', 'idx': 0}"
<stdlib>\json\decoder.py,358,"        return obj, end",,"{'s': '[]', 'end': 2, 'self': '<json.decoder.JSONDecoder object at 0x0000014038FA9BE0>', 'obj': [], 'idx': 0}"
<stdlib>\json\decoder.py,340,"        end = _w(s, end).end()",,"{'obj': [], 'end': 2, 'self': '<json.decoder.JSONDecoder object at 0x0000014038FA9BE0>', '_w': '<built-in method match of _sre.SRE_Pattern object at 0x0000014038FBB1B0>', 's': '[]'}"
<stdlib>\json\decoder.py,341,        if end != len(s):,,"{'obj': [], 'end': 2, 'self': '<json.decoder.JSONDecoder object at 0x0000014038FA9BE0>', '_w': '<built-in method match of _sre.SRE_Pattern object at 0x0000014038FBB1B0>', 's': '[]'}"
<stdlib>\json\decoder.py,343,        return obj,,"{'obj': [], 'end': 2, 'self': '<json.decoder.JSONDecoder object at 0x0000014038FA9BE0>', '_w': '<built-in method match of _sre.SRE_Pattern object at 0x0000014038FBB1B0>', 's': '[]'}"
example.py,11,    i = 5,,"{'result': [], 'a': 2}"
example.py,12,    while (i > 0):,,"{'i': 5, 'result': [], 'a': 2}"
example.py,13,        a = square(a + 1),,"{'i': 5, 'result': [], 'a': 2}"
example.py,6,    return x * x,,{'x': 3}
example.py,14,        result.append(a),,"{'i': 5, 'result': [], 'a': 9}"
example.py,15,        i -= 1,,"{'i': 5, 'result': [9], 'a': 9}"
example.py,12,    while (i > 0):,,"{'i': 4, 'result': [9], 'a': 9}"
example.py,13,        a = square(a + 1),,"{'i': 4, 'result': [9], 'a': 9}"
example.py,6,    return x * x,,{'x': 10}
example.py,14,        result.append(a),,"{'i': 4, 'result': [9], 'a': 100}"
example.py,15,        i -= 1,,"{'i': 4, 'result': [9, 100], 'a': 100}"
example.py,12,    while (i > 0):,,"{'i': 3, 'result': [9, 100], 'a': 100}"
example.py,13,        a = square(a + 1),,"{'i': 3, 'result': [9, 100], 'a': 100}"
example.py,6,    return x * x,,{'x': 101}
example.py,14,        result.append(a),,"{'i': 3, 'result': [9, 100], 'a': 10201}"
example.py,15,        i -= 1,,"{'i': 3, 'result': [9, 100, 10201], 'a': 10201}"
example.py,12,    while (i > 0):,,"{'i': 2, 'result': [9, 100, 10201], 'a': 10201}"
example.py,13,        a = square(a + 1),,"{'i': 2, 'result': [9, 100, 10201], 'a': 10201}"
example.py,6,    return x * x,,{'x': 10202}
example.py,14,        result.append(a),,"{'i': 2, 'result': [9, 100, 10201], 'a': 104080804}"
example.py,15,        i -= 1,,"{'i': 2, 'result': [9, 100, 10201, 104080804], 'a': 104080804}"
example.py,12,    while (i > 0):,,"{'i': 1, 'result': [9, 100, 10201, 104080804], 'a': 104080804}"
example.py,13,        a = square(a + 1),,"{'i': 1, 'result': [9, 100, 10201, 104080804], 'a': 104080804}"
example.py,6,    return x * x,,{'x': 104080805}
example.py,14,        result.append(a),,"{'i': 1, 'result': [9, 100, 10201, 104080804], 'a': 10832813969448025}"
example.py,15,        i -= 1,,"{'i': 1, 'result': [9, 100, 10201, 104080804, 10832813969448025], 'a': 10832813969448025}"
example.py,12,    while (i > 0):,,"{'i': 0, 'result': [9, 100, 10201, 104080804, 10832813969448025], 'a': 10832813969448025}"
example.py,16,    return result,,"{'i': 0, 'result': [9, 100, 10201, 104080804, 10832813969448025], 'a': 10832813969448025}"
```


## FAQ

### Why not just use [PySnooper](https://github.com/cool-RR/PySnooper)?

Because I didn't know about that project until development I was almpost done with the first version.

Still, this has a couple of design choices that makes spypy slightly friendlier for some usecases:

* More flexible output: snapshots are stored as intermediate representation rather than writing immediately
    * This is of course massively more memory-intensive, so this may need to change in the future
* More direct API (`tracer.trace(function)` vs using a decorator on a function)
