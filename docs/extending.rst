Extending json-five
===================


The ``json`` way
----------------


``json5.load`` and ``json5.loads`` support a similar interface to the stdlib ``json`` module. Specifically,
you can provide the following arguments that have the same meaning as in ``json.load``:

- ``parse_int``
- ``parse_float``
- ``parse_constant``
- ``object_hook``
- ``object_pairs_hook``

This is convenient if you have existing code that uses these arguments with the ``json`` module, but want to also
support JSON5. These options are also useful as a simple way to customize parsing of json types.

However, this package does not support the ``cls`` keyword. If you want to implement custom serializers/deserializers,
read on about custom loaders/dumpers


Custom Loaders and Dumpers
--------------------------

This package uses "Loaders" as part of the deserialization of JSON text to Python. "Dumpers" are used to
serialize Python objects to JSON text.

The entry points for loaders and dumpers are the ``load`` and ``dump`` methods, respectively.
You can override these methods to implement custom loading of models or dumping of objects.

Extending the default loader
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The default loader takes in a model and produces, in the default case, Python objects.

As a simple example, you can extend the default loader with your own to customize loading of lists. Here,
I'll create a custom loader that, when it encounters an array (``json5.model.JSONArray``) with with only one value, it will return
the single value, rather than a single-item array.

.. code-block::

    from json5.loader import DefaultLoader, loads
    from json5.model import JSONArray


    class MyCustomLoader(DefaultLoader):
        def load(self, node):
            if isinstance(node, JSONArray):
                return self.json_array_to_python(node)
            else:
                return super().load(node)

        def json_array_to_python(self, node):
            if len(node.values) == 1:
                return self.load(node.values[0])
            else:
                return super().json_array_to_python(node)

The ``loads`` function accepts a ``loader`` keyword argument, where the custom loader can be passed in.

.. code-block::

    json_string = "{foo: ['bar', 'baz'], bacon: ['eggs']}"
    loads(json_string)  # Using the regular default loader
    # {'foo': ['bar', 'baz'], 'bacon': ['eggs']}

    loads(json_string, loader=MyCustomLoader())  # use the custom loader instead
    # {'foo': ['bar', 'baz'], 'bacon': 'eggs'}


Extending the default dumper
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Extending the dumper follows a similar principle as extending the loader.

As an example, I'll make a custom dumper that dumps booleans ``True`` and ``False`` to integers instead of the
JSON ``true`` or ``false``.

.. code-block::

    from json5.dumper import DefaultDumper, dumps

    class MyCustomDumper(DefaultDumper):
        def dump(self, node):
            if isinstance(node, bool):
                return self.bool_to_json(node)
            else:
                return super().dump(node)

        def bool_to_json(self, node):
            super().dump(int(node.value))

And you can see the effects

.. code-block::

    >>> dumps([True, False])
    '[true, false]'
    >>> dumps([True, False], dumper=MyCustomDumper())
    '[1, 2]'


Other loaders/dumpers and tools
-------------------------------

Besides the default loader, there is also the ``ModelLoader`` which simply returns the raw model
with no additional processing.

Besides the default dumper, there is also the ``ModelDumper`` which takes a model and serializes it to JSON.

The ``json5.dumper.modelize`` function can take python objects and convert them to a model.


.. code-block::

    from json5.dumper import modelize
    obj = ['foo', 123, True]
    modelize(obj)

The resulting model:

.. code-block::

    JSONArray(
        values=[
            SingleQuotedString(characters='foo', raw_value="'foo'"),
            Integer(raw_value='123', value=123, is_hex=False),
            BooleanLiteral(value=True),
        ],
        trailing_comma=None,
    )
