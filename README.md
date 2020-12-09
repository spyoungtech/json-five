# json-five

JSON5 for Python

[![Documentation Status](https://readthedocs.org/projects/json-five/badge/?version=latest)](https://json-five.readthedocs.io/en/latest/?badge=latest) 
[![Build Status](https://travis-ci.com/spyoungtech/json-five.svg?branch=master)](https://travis-ci.com/spyoungtech/json-five) 
[![version](https://img.shields.io/pypi/v/json-five.svg?colorB=blue)](https://pypi.org/project/json-five/) 
[![pyversion](https://img.shields.io/pypi/pyversions/json-five.svg?)](https://pypi.org/project/json-five/) 
[![Coverage](https://coveralls.io/repos/github/spyoungtech/json-five/badge.svg?branch=master)](https://coveralls.io/github/spyoungtech/json-five?branch=master)

## Installation

```
pip install json-five
```

This project requires Python 3.6 or newer.

## Usage

**NOTE:** the import name is different from the install name (sorry, many were taken already)

```python
>>> import json5
>>> json_text = """{ // This is a JSON5 comment
"foo": "bar" /* this is a JSON5 block
comment that can span lines /*
"bacon": "eggs"
}
"""
>>> json5.loads(json_text)
{"foo": "bar", "bacon": "eggs"}
```

You can also use `json5.tool` for validating json.

```
python3 -m json5.tool < myfile.json5
```

See also the [full documentation](https://json-five.readthedocs.io/en/latest/)

## Key features

- Supports the JSON5 spec
- Supports similar interfaces to stdlib `json` module
- Supports round-trip preservation of comments
- Tries to find _all_ syntax errors at once (instead of raising on the first error encountered)


## Status

This project is still in early stages of development. Check the [issues](https://github.com/spyoungtech/json-five/issues) 
page to see known bugs and unimplemented features.
