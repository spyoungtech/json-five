import subprocess
import pytest
import io
@pytest.mark.parametrize('json_string', [
"""{"foo":"bar"}""",
"""{"foo": "bar"}""",
"""{"foo":"bar","bacon":"eggs"}""",
"""{"foo":  "bar", "bacon" :  "eggs"}""",
"""["foo","bar","baz"]""",
"""[ "foo", "bar"  , "baz"   ]""",
"""{"foo":\n "bar"\n}""",
"""{"foo": {"bacon": "eggs"}}""",
"""   {"foo":"bar"}""",
"""{"foo": "bar"}   """,
"""{'foo': 'bar'}""",
"""{"foo": 'bar'}""",
"""{"foo": "bar",}""",
"""["foo","bar", "baz",]""",
"""["foo", "bar", "baz", ]""",
"""["foo", "bar", "baz"  ,]""",
"""[["foo"], ["foo","bar"], "baz"]""",
"""{unquoted: "foo"}""",
"""{unquoted: "foo"}""",
"""["foo"]""",
"""["foo" , ]""",
])
def test_tool(json_string):
    r = subprocess.run(['python3', '-m', 'json5.tool'], text=True, input=json_string, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    assert r.stdout[:-1] == json_string
