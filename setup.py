"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
"""

from setuptools import setup, find_packages
import pathlib

CHANGES = """

## Version 1.12.0:
- Support style (and hence attrib) on Stores and Channels.

## Version 1.11.1.post2:

Bug fixes:
- Apply attribs on frames.
- Attribs are matched by whole names, so e.g. DATA and DATABASE will work.

Improvements:
- 'make install' to install locally.
- CHANGES.md is read by setup.py to deduce the version.

## Version 1.11.0:

- Keyword "attrib" to define styles.

## Version 1.10.1:

- When item text is numbered, add newline after the number.

## Version 1.9.1:

- Add troubleshooting in README.md.

## Version 1.9.0:

- Allow line continuation with a trailing backslash

## Version 1.8.0:

- Add frames

## Version 1.7.1:

- Support continuous back- and relaxed- flows.

## Version 1.7.0:

- Add continuous flow (cflow or -->>).
- Add control (may only connect to signals).

## Version 1.6.0:

- Dependencies:
  - items with name #SNIPPET:[NAME] or FILE:[NAME] refer to another graph,
  - referred item is rendered "ghosted",
  - dependencies are checked (unless --no-check-dependencies is passed).
- Add graph title (unless --no-graph-title is passed).
- Error in snippets of MD files: display line number relative to MD file (not snippet).

## Version 1.5.0:

- Wrap labels by `style item-text-width N` (default N=20).
- and `style connection-text-width N` (default N=14).

## Version 1.4.1:

- Processes have very light grey backgrounds.
- Add the 'none' item type.
- Connections with reversed direction affect the items placements.
- A '?' postfix to a connection, removes the edge constraint.
- Fix formatting of '\n' for Store and Channel (which are HTML nodes).
- Colorize error messages.
- Add drawable attributes as [ATTRS...] prefix before labels.

## Version 1.3.x:

- Style vertical: is supported.
- Style context: for context (top-level) diagrams.
- Add undirected flow (uflow aka '--').

## Version 1.2.3

- Snippet reference and ungenerated snippet were marked with '<'; now
  use '#' instead.
- Detect include (infinite) recursions and print error.
- Can print its own version.

## Version 1.1.1

- Fix bug with left/bidir arrows.

## Version 1.1.0

- Upon error, print error stack trace.
- Items: label can be ommitted.
- Connections: syntactic sugars with arrows.

## Version 1.0.0

- Initial release.
"""

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

# extract version
lines = CHANGES.splitlines()
lines = [l[2:] for l in lines if l.startswith('##')]
version = lines[0].strip().split(':', 1)[0].split()[-1].strip()

setup(
    name="data-flow-diagram",
    version=version,
    description="Commandline tool to generate data flow diagrams from text",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pbauermeister/dfd",
    author="Pascal Bauermeister",
    author_email="pascal.bauermeister@gmail.com",
    classifiers=[
        # https://pypi.org/classifiers/ :
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Information Technology",
        "Topic :: Software Development",
        "Topic :: Software Development :: Documentation",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
    ],
    keywords="diagram-generator, development, tool",
    license="GNU General Public License v3 (GPLv3)",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10, <4",
    install_requires=[],
    extras_require={
        "dev": ["check-manifest"],
        "test": ["coverage"],
    },
    package_data={
        #        "data_flow_diagram": ["tbdpackage__data.dat"],
    },
    #    data_files=[('data_flow_diagram', ["VERSION"])],
    # The following would provide a command called `data-flow-diagram` which
    # executes the function `main` from this package when invoked:
    entry_points={
        "console_scripts": [
            "data-flow-diagram=data_flow_diagram:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/pbauermeister/dfd/issues",
        #        "Funding": "https://donate.pypi.org",
        #        "Say Thanks!": "http://saythanks.io/to/example",
        "Source": "https://github.com/pbauermeister/dfd",
    },
)
