from json5 import loads, load, JSON5DecodeError
import os
import pytest
from io import open

tests_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../json5-tests'))

error_specs = []
specs = []

for root,dirs,files in os.walk(tests_path):
    for f in files:
        if f.endswith('.json5') or f.endswith('.json'):
            specs.append(os.path.join(root, f))
        elif f.endswith('.txt'):
            error_spec = f.replace('.txt', '.errorSpec')
            error_specs.append((os.path.join(root, f), os.path.join(root, error_spec)))

@pytest.mark.parametrize('fp', specs)
def test_official_files(fp):
    try:
        load(open(fp, encoding='utf-8'))
    except JSON5DecodeError:
        if 'todo' in fp:
            pytest.mark.xfail("TODO files expected to fail")
        else:
            raise

@pytest.mark.parametrize(('input_file', 'expected'), error_specs)
def test_official_error_specs(input_file, expected):
    if 'octal' in input_file:
        pytest.mark.xfail("Octals are dumb")
        return
    with pytest.raises(JSON5DecodeError) as exc_info:
        load(open(input_file, encoding='utf-8'))