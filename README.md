# json-five

JSON5 for Python

[![Documentation Status](https://readthedocs.org/projects/json-five/badge/?version=latest)](https://json-five.readthedocs.io/en/latest/?badge=latest)
[![Build](https://github.com/spyoungtech/json-five/actions/workflows/unittests.yml/badge.svg)](https://github.com/spyoungtech/json-five/actions/workflows/unittests.yaml)
[![version](https://img.shields.io/pypi/v/json-five.svg?colorB=blue)](https://pypi.org/project/json-five/)
[![pyversion](https://img.shields.io/pypi/pyversions/json-five.svg?)](https://pypi.org/project/json-five/)
[![Coverage](https://coveralls.io/repos/github/spyoungtech/json-five/badge.svg?branch=main)](https://coveralls.io/github/spyoungtech/json-five?branch=main)

## Installation

```
pip install json-five
```

This project requires Python 3.8+


## Key features

- Supports the JSON5 spec
- Supports similar interfaces to stdlib `json` module
- Provides an API for working with abstract model representations of JSON5 documents.
- Supports round-trip loading, editing, and dumping, preserving non-data elements such as comments (in model-based load/dump)



# Usage

**NOTE:** the import name is `json5` which differs from the install name.


For basic loading/dumping, the interface is nearly identical to that of the `json` module.
```python
import json5
json_text = """{ // This is a JSON5 comment
"foo": "bar" /* this is a JSON5 block
comment that can span lines */
bacon: "eggs"  // unquoted Identifiers also work
}
"""
print(json5.loads(json_text))
# {"foo": "bar", "bacon": "eggs"}

with open('myfile.json5') as f:
    data = json5.load(f)
```

For loading JSON5, the same parameters `object_hook`, `object_pairs_hook` and `parse_*` keyword arguments are available
here for `load`/`loads`.

Additionally, a new hook, `parse_json5_identifiers`, is available to help users control the
output of parsing identifiers. By default, JSON5 Identifiers in object keys are returned as a `JsonIdentifier` object,
which is a subclass of `str` (meaning it's compatible anywhere `str` is accepted).
This helps keep keys the same round-trip, rather than converting unquoted identifiers into
 strings:

```python
>>> text = '{bacon: "eggs"}'
>>> json5.dumps(json5.loads(text)) == text
True
```

You can change this behavior with the `parse_json5_identifiers` argument with a callable that receives the `JsonIdentifier` object
and its return value is used instead. For example, you can specify `parse_json5_identifiers=str` to convert identifiers
to strings.

```python
>>> json5.dumps(json5.loads(text, parse_json5_identifiers=str))
'{"bacon": "eggs"}'
```


## Custom loaders; Abstract JSON5 Models

**Note:** the underlying model API and tokens are not stable and are subject to breaking changes, even in minor releases.

json-five also features an API for representing JSON5 as an abstract model. This enables a wide degree of capabilities for
various use-cases, such as linters, formatters, custom serialization/deserialization, and more.


Example: a simple model

```python
from json5.loader import loads, ModelLoader
json_string = """{"foo": "bar"}"""
model = loads(json_string, loader=ModelLoader())
```
The model object looks something like this:
```python
JSONText(
    value=JSONObject(
        key_value_pairs=[
            KeyValuePair(
                key=DoubleQuotedString(
                    characters="foo",
                    raw_value='"foo"',
                    tok=JSON5Token(
                        type="DOUBLE_QUOTE_STRING",
                        value='"foo"',
                        lineno=1,
                        index=1,
                        end=None,
                    ),
                ),
                value=DoubleQuotedString(
                    characters="bar",
                    raw_value='"bar"',
                    tok=JSON5Token(
                        type="DOUBLE_QUOTE_STRING",
                        value='"bar"',
                        lineno=1,
                        index=8,
                        end=None,
                    ),
                ),
                tok=JSON5Token(
                    type="DOUBLE_QUOTE_STRING",
                    value='"foo"',
                    lineno=1,
                    index=1,
                    end=None,
                ),
            )
        ],
        trailing_comma=None,
    )
)
```


It is possible to make edits to the model, which will affect the output when dumped using the model dumper. However,
there is (currently) no validation to ensure your model edits won't result in invalid JSON5 when dumped.

You may also implement custom loaders and dumpers to control serialization and deserialization. See the [full documentation](https://json-five.readthedocs.io/en/latest/extending.html#custom-loaders-and-dumpers)
for more information.


# Status

This project currently fully supports the JSON5 spec and its interfaces for loading and dumping JSON5 is stable as of v1.0.0.
There is still active development underway, particularly for the underlying abstract JSON5 model representations and
ability to perform edits using the abstract model.
