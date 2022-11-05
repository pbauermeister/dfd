import io
import unittest
import sys
import contextlib

import inputs

sys.path.insert(0, "src")

from data_flow_diagram import parse_args, main
from data_flow_diagram import parser, scanner
from data_flow_diagram import model
from data_flow_diagram.markdown import extract_snippets

def is_svg(text: str) -> bool:
    text = text.strip()
    return text.startswith('<?xml') and text.endswith('</svg>')


class UnitTest(unittest.TestCase):

    def test_parse_args(self) -> None:

        # replace cmdline args
        a1 = 'my-file'
        old_argv = sys.argv
        sys.argv = [old_argv[0]] + [a1]

        try:
            args = parse_args()
        finally:
            # restore
            sys.argv = old_argv

        keys = set(['INPUT_FILE',
                    'output_file',
                    'markdown',
                    'format',
                    'percent_zoom',
                    'background_color',
                    'debug',
                    ])
        self.assertSetEqual(
            set(args.__dict__.keys()), keys,
            'Commandline args mismatch')
        self.assertEqual(
            args.INPUT_FILE, a1,
            'Commandline positional arg mismatch')

    def test_input_md(self) -> None:
        result = extract_snippets(inputs.MD_OK)
        expected = [
            model.Snippet(**inputs.MD_EXPECTED[0]),
            model.Snippet(**inputs.MD_EXPECTED[1]),
        ]
        self.assertSequenceEqual(
            result, expected,
            'Extraction of snippets in MD text')

    def test_output_stdout(self) -> None:
        old_stdin = sys.stdin
        sys.stdin = io.StringIO("process P Process")  # DFD

        # replace cmdline args
        old_argv = sys.argv
        sys.argv = [old_argv[0]] + []

        f = io.StringIO()
        try:
            with contextlib.redirect_stdout(f):
                main()
        finally:
            # restore
            sys.stdin = old_stdin
            sys.argv = old_argv

        # get and analyze SVG
        out = f.getvalue().strip()
        self.assertTrue(is_svg(out),
                         'Output to stdout is not SVG')

    def test_parse_all_syntax_ok(self) -> None:
        l = scanner.scan(None, inputs.ALL_SYNTAX_OK)
        try:
            parser.parse(l)
        except model.DfdException as e:
            self.fail(f'Unexpected syntax error: {e}')

    def test_parse_syntax_error(self) -> None:
        l = scanner.scan(None, inputs.SYNTAX_ERROR)
        with self.assertRaises(model.DfdException,
                               msg='Undetected syntax error'):
            parser.parse(l)

    def test_parse_duplicate_item_error(self) -> None:
        l = scanner.scan(None, inputs.DUPLICATE_ITEM_ERROR)
        statements = parser.parse(l)
        with self.assertRaises(model.DfdException,
                               msg='Undetectd duplicate item name'):
            parser.check(statements)

    def test_parse_missing_ref_error(self) -> None:
        l = scanner.scan(None, inputs.MISSING_REF_ERROR)
        statements = parser.parse(l)
        with self.assertRaises(model.DfdException,
                               msg='Undetectd missing reference'):
            parser.check(statements)

    def test_parse_double_error(self) -> None:
        l = scanner.scan(None, inputs.DOUBLE_STAR_ERROR)
        statements = parser.parse(l)
        with self.assertRaises(model.DfdException,
                               msg='Undetectd double * reference'):
            parser.check(statements)



if __name__ == '__main__':
    unittest.main()
