import argparse
from json5 import loads, dump, load
from json5.loader import ModelLoader
from json5.dumper import ModelDumper
import sys


def main():
    prog = 'python -m json5.tool'
    description = ('Command line interface for the json5 module '
                   'analogous to the json.tool CLI.')
    parser = argparse.ArgumentParser(prog=prog, description=description)
    parser.add_argument('infile', nargs='?',
                        type=argparse.FileType(encoding="utf-8"),
                        help='a JSON file to be validated',
                        default=sys.stdin)
    parser.add_argument('outfile', nargs='?',
                        type=argparse.FileType('w', encoding="utf-8"),
                        help='write the output of infile to outfile',
                        default=sys.stdout)
    parser.add_argument('--json-lines', action='store_true', default=False,
                        help='parse input using the JSON Lines format.')
    options = parser.parse_args()

    dump_args = {
        'dumper': ModelDumper()
    }

    with options.infile as infile, options.outfile as outfile:
        try:
            if options.json_lines:
                objs = (loads(line, loader=ModelLoader()) for line in infile)
            else:
                objs = (load(infile, loader=ModelLoader()), )
            for obj in objs:
                dump(obj, outfile, **dump_args)
                outfile.write('\n')
        except ValueError as e:
            raise SystemExit(e)


if __name__ == '__main__':
    try:
        main()
    except BrokenPipeError as exc:
        sys.exit(exc.errno)