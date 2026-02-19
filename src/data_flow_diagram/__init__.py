"""data_flow_diagram — package interface.

Re-exports the public API so that existing entry points and imports
continue to work:
  - setup.py console_scripts: ``data_flow_diagram:main``
  - dev wrapper: ``./data-flow-diagram`` calls ``main()``
  - tests: ``from data_flow_diagram import parse_args, main``
"""

from .cli import VERSION, main, parse_args

__all__ = ["VERSION", "main", "parse_args"]
