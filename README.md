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

This project has just one requirement: the [`sly`](https://github.com/dabeaz/sly) package.

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

See also the [full documentation](https://json-five.readthedocs.io/en/latest/)

## Project goals

- support a similar interface to the `json` module with support for JSON5 sources
- support round-trip preservation of comments

## Status/milestones

This project is in very early stages of development. The following are some 
milestones that hopefully will be able to be marked as done as development progresses.

- [x] parse json5 to Python (ignoring comments)
  - [x] line comments
  - [x] block comments
  - [x] numeric literals
  - [x] trailing commas for arrays and objects
  - [x] line continuations
  - [x] ecma identifiers as object keys
  - [x] leading plus for numbers
  - [x] single quoted strings
  - [x] escape characters in strings
- [x] dump python to JSON (no comment support)
  - [x] indent style (that matches `json`)
  - [ ] style options (quotes, trailing commas, etc)
  - [ ] helper classes for dumping types as other literals (hexadecimal numbers, identifiers, etc)
  - [x] load/loads to support similar options to `json` (e.g. `object_hook`, `parse_x`, etc)
  - [ ] dump/dumps to support similar options to `json` module (e.g. hooks, `ensure_ascii`, etc)
  - [ ] string escapes according to quote style
- [ ] support manipulation of json model (e.g. to add/edit comments)
- [ ] dump json model with comments
- [ ] preserve comments when loading json5 (round-trip support)

...

- [ ] Optimize with a C/Cython version

## How fast is it?

It's nowhere close to the C-optimized `json` stdlib module. We may get closer to that 
benchmark if/when we rewrite parts with Cython.

In my own limited testing, as of v0.0.2, this module is about 10-450x slower than the stdlib C-optimized `json` 
and about 10-50x slower than the stdlib pure python version of `json`.

I expect this to slow down marginally when round-trip comment preservation is implemented.
