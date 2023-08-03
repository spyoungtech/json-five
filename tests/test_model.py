import ast

import pytest

import json5.loader
import json5.model

TEST_TEXT = '''\
{
    "string_on_same_line":     "string on same line",
          "multiline_dq_string": "this line has a \
continuation",  
      "leadingDecimalPoint": .8675309  ,    
      "andTrailing":     8675309.,  
    "trailingComma": 'in objects',   
        "backwardsCompatible": "with JSON",
}
'''

model = json5.loads(TEST_TEXT, loader=json5.loader.ModelLoader())
tree = ast.parse(TEST_TEXT)
ast_nodes = [
    node for node in list(ast.walk(tree)) if not isinstance(node, (ast.Expr, ast.Load, ast.Module, ast.UnaryOp))
]
json5_nodes = [
    node
    for node in list(json5.model.walk(model))
    if not isinstance(node, (json5.model.TrailingComma, json5.model.JSONText))
]

assert len(ast_nodes) == len(json5_nodes)


@pytest.mark.parametrize('ast_node, json5_node', list(zip(ast_nodes, json5_nodes)))
@pytest.mark.parametrize(
    'attr_name',
    [
        'col_offset',
        'end_col_offset',
        'lineno',
        'end_lineno',
    ],
)
def test_node_attribute_accuracy(attr_name: str, ast_node, json5_node):
    assert getattr(json5_node, attr_name) == getattr(
        ast_node, attr_name
    ), f'{attr_name} did not match {ast_node!r}, {json5_node!r}'
