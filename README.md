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