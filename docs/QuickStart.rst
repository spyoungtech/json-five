QuickStart
==========

Installation
------------

.. code-block::

   pip install json-five


Basic Usage
-----------

Suppose you have a JSON5 compliant file ``my-json-file.json``

.. code-block::

    // This is a JSON5 file!
    {'foo': 'bar'}

You can load this file to Python like so:

.. code-block::

   import json5
   with open('my-json-file.json') as f:
       data = json5.load(f)

You can also work directly with strings

.. code-block::

    import json5
    json_string = '{json5 /* identifiers dont need quotes */: "values do though"}'
    data = json5.loads(json_string)


Want to do more? Check out :doc:`/extending` to dive deeper!
