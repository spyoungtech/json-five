# json-five

JSON5 for Python

## Usage

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
- [ ] dump python to JSON (no comment support)
  - [x] indent style (that matches `json`)
  - [ ] style options (quotes, trailing commas, etc)
  - [ ] helper classes for dumping types as other literals (hexadecimal numbers, identifiers, etc)
  - [ ] support similar options to `json` (e.g. `object_hook`, `parse_x`, `strict`, `ensure_ascii`, etc)
  - [ ] string escapes according to quote style
- [ ] support manipulation of json model (e.g. to add/edit comments)
- [ ] dump json model with comments
- [ ] preserve comments when loading json5 (round-trip support)
