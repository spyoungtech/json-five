How this package works
======================

This is an overview of how the internals of this package work. The code demonstrated here is not
necessarily intended to be used by users!

If you're wondering how to use this package, see :doc:`/QuickStart` instead.



Deserializing JSON to Python; the journey
-----------------------------------------

The first step in deserialization is tokenizing. Text, assuming it is conforming to the JSON5 spec,
is parsed into _tokens_. The tokens are then _parsed_ to produce a representative _model_ of the JSON structure.
Finally, that model is _loaded_ where each node in the model is turned into an instance of a Python data type.

Let's explore this process interactively.

tokenizing
^^^^^^^^^^

Tokenizing is the first step in turning JSON text into Python objects. Let's look at tokenizing
a very simple empty JSON object ``{}``

.. code-block::

    >>> from json5.tokenizer import tokenize
    >>> json_string = "{}"
    >>> tokens = tokenize(json_string)
    >>> for token in tokens:
    ...     print(token)
    ...
    Token(type='LBRACE', value='{', lineno=1, index=0)
    Token(type='RBRACE', value='}', lineno=1, index=1)

As you can see, this broke down into two tokens: the left brace and the right brace.

For good measure, let's see a slightly more complex tokenization

.. code-block::

    for token in tokenize("{foo: 'bar'}"):
        print(token)

    Token(type='LBRACE', value='{', lineno=1, index=0)
    Token(type='NAME', value='foo', lineno=1, index=1)
    Token(type='COLON', value=':', lineno=1, index=4)
    Token(type='WHITESPACE', value=' ', lineno=1, index=5)
    Token(type='SINGLE_QUOTE_STRING', value="'bar'", lineno=1, index=6)
    Token(type='RBRACE', value='}', lineno=1, index=11)

These tokens will be used to build a model in the next step.


Parsing and models
^^^^^^^^^^^^^^^^^^

As the text is processed into tokens, the stream of tokens is parsed into a model representing the JSON structure.

Let's start with the same simple example of an empty JSON object ``{}``

.. code-block::

    >>> from json5.tokenizer import tokenize
    >>> from json5.parser import parse_tokens
    >>> tokens = tokenize("{}")
    >>> model = parse_tokens(tokens)
    >>> model
    JSONText(value=JSONObject(key_value_pairs=[], trailing_comma=None))

The tokens were parsed to produce a model. Each production (part) in the model more or less represents a part of the
`JSON5 grammar`_. ``JSONText`` is always the root production of the model for any JSON5 document.

Let's look at a more complex model for the JSON text ``{foo: 0xC0FFEE}`` -- This model has been 'prettified' for this doc:

.. code-block::

    JSONText(
        value=JSONObject(
            key_value_pairs=[
                KeyValuePair(
                    key=Identifier(name='foo'),
                    value=Integer(raw_value='0xC0FFEE', value=12648430, is_hex=True),
                )
            ],
            trailing_comma=None,
        )
    )


You can also build model objects 'manually' without any source text.

.. code-block::

    from json5.model import *
    model = JSONText(value=JSONObject(KeyValuePair(key=Identifier('bacon'), value=Infinity())))


Loading
^^^^^^^

Once we have a model in-hand, we can use it to generate Python object representation from the model. To do this,
specialized classes, called Loaders, are used. Loaders take a model and produce something else, like Python data types.


In this example, we'll just create a model instead of parsing one from text and turn it into Python using the
default loader (the default loader is used when calling ``loads`` by default.

.. code-block::

    >>> from json5.loader import DefaultLoader
    >>> from json5.model import *
    >>> loader = DefaultLoader()
    >>> model = JSONText(value=JSONObject(KeyValuePair(key=Identifier('bacon'), value=Infinity())))
    >>> loader.load(model)
    {'bacon': inf}



Serializing to JSON
-------------------

Objects can be serialized to JSON using _dumpers_. A dumper takes and object and writes JSON text representing the object.
The default dumper dumps python objects directly to JSON text.

.. code-block::

    >>> from json5 import dumps
    >>> dumps(['foo', 'bar', 'baz'])
    '["foo", "bar", "baz"]'



.. _JSON5 grammar: https://spec.json5.org/#grammar


