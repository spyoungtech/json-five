import os
import re
from collections import namedtuple

import pytest

from json5 import dumps
from json5 import JSON5DecodeError
from json5 import load
from json5 import loads
from json5.dumper import ModelDumper
from json5.loader import ModelLoader

tests_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../json5-tests'))

error_specs = []
specs = []

for root, dirs, files in os.walk(tests_path):
    for f in files:
        if f.endswith('.json5') or f.endswith('.json'):
            specs.append(os.path.join(root, f))
        elif f.endswith('.txt') or f.endswith('.js'):
            error_spec = f.replace('.txt', '.errorSpec').replace('.js', '.errorSpec')
            error_specs.append((os.path.join(root, f), os.path.join(root, error_spec)))


@pytest.mark.parametrize('fp', specs)
def test_official_files(fp):
    if not os.path.exists(tests_path):
        pytest.mark.skip("Tests repo was not present in expected location. Skipping.")
        return
    load(open(fp, encoding='utf-8'))


@pytest.mark.parametrize('fp', specs)
def test_official_files_rt_dumps_no_error(fp):
    if not os.path.exists(tests_path):
        pytest.mark.skip("Tests repo was not present in expected location. Skipping.")
    with open(fp, encoding='utf-8') as f:
        json_string = f.read()
    dumps(loads(json_string))


@pytest.mark.parametrize('fp', specs)
def test_official_files_rt_model(fp):
    if not os.path.exists(tests_path):
        pytest.mark.skip("Tests repo was not present in expected location. Skipping.")
    with open(fp, encoding='utf-8') as f:
        json_string = f.read()
    assert dumps(loads(json_string, loader=ModelLoader()), dumper=ModelDumper()) == json_string


@pytest.mark.parametrize(('input_file', 'expected'), error_specs)
def test_official_error_specs(input_file, expected):
    if not os.path.exists(tests_path):
        pytest.mark.skip("Tests repo was not present in expected location. Skipping.")
        return
    with pytest.raises(JSON5DecodeError):
        load(open(input_file, encoding='utf-8'))


@pytest.mark.parametrize(('input_file', 'expected'), error_specs)
def test_official_error_specs(input_file, expected):
    ErrorInfo = namedtuple('ErrorInfo', field_names=['line', 'col', 'at'])
    if not os.path.exists(tests_path):
        pytest.mark.skip("Tests repo was not present in expected location. Skipping.")
        return
    if any(name in input_file for name in ['top-level-inline-comment.txt', 'unescaped-multi-line-string.txt']):
        pytest.xfail("We make better error messages for these")
    if os.path.exists(expected):
        errorspec = load(open(expected, encoding='utf-8'))
    else:
        pytest.mark.skip("No error spec")
        return

    with pytest.raises(JSON5DecodeError) as exc_info:
        load(open(input_file, encoding='utf-8'))

    at = errorspec['at']
    lineno = errorspec['lineNumber']
    col = errorspec['columnNumber']
    # msg = errorspec['message']
    exc_message = str(exc_info.value)
    exc_lineno_match = re.search(r'line (\d+)', exc_message)
    if exc_lineno_match:
        exc_lineno = int(exc_lineno_match.groups()[0])
    else:
        exc_lineno = None
    exc_col_match = re.search(r'column (\d+)', exc_message)
    if exc_col_match:
        exc_col = int(exc_col_match.groups()[0])
    else:
        exc_col = None
    exc_index_match = re.search(r'char (\d+)', exc_message)
    if exc_index_match:
        exc_index = int(exc_index_match.groups()[0])
    else:
        exc_index = None
    assert ErrorInfo(exc_lineno, exc_col, exc_index) == ErrorInfo(lineno, col, at - 1), f"{input_file} {exc_message}"
