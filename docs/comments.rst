Working with comments
=====================

In order to work with comments, you must work with the raw model.

Each node in the model has two special attributes: ``.wsc_before`` and ``.wsc_after``. These attributes are a list of
any whitespace or comments that appear before or after the node.

.. code-block::

    from json5.loader import loads, ModelLoader
    from json5.dumper import dumps, ModelDumper
    from json5.model import BlockComment
    json_string = """{"foo": "bar"}"""
    model = loads(json_string, loader=ModelLoader())
    print(model.value.key_value_pairs[0].value.wsc_before)  # [' ']
    model.value.key_value_pairs[0].key.wsc_before.append(BlockComment("/* comment */"))
    dumps(model, dumper=ModelDumper()) # '{/* comment */"foo": "bar"}'


This section will be expanded with time, the API for working with comments will likely change alot in future
versions.