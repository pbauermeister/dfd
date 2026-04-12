# DFD — Data Flow Diagrams as Code

[![CI](https://github.com/pbauermeister/dfd/actions/workflows/ci.yml/badge.svg)](https://github.com/pbauermeister/dfd/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/data-flow-diagram)](https://pypi.org/project/data-flow-diagram/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

Describe system architectures as text, get diagrams as SVG, PNG, PDF, and
more. Version-controlled, diffable, no GUI needed.

DFD generates [Data Flow Diagrams](https://en.wikipedia.org/wiki/Data-flow_diagram)
from a simple text-based DSL, rendered via [Graphviz](https://graphviz.org/).
It supports the SA/SD and SA/RT methodologies (Structured Analysis /
Structured Design, with real-time extensions) as described by Edward Yourdon.

![Complete example](https://raw.githubusercontent.com/pbauermeister/dfd/main/img/hero.svg "Complete example — an SA/RT data acquisition system")

The diagram above is generated from this input:

```
process   Acquire         Acquire data
process   Compute
control   Control
entity    Device
store     Config          Configuration
channel   API

*         ::>  Control    clock
Control   <::  *          enable
Control   <::  *          disable
Control   ::>? Acquire    sampling

Device    ->>  Acquire    continuous raw data
Acquire   -->  Compute    raw records
Config    <->  Compute    parameters
Compute   -->  API        records
```

## Features

| Feature                     | Description                                                                                                                                     |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **SA/RT** support           | Signals, control processes, and channels for real-time and embedded systems                                                                     |
| **Context** diagrams        | Generate a top-level SA/SD context diagram (`style context`)                                                                                    |
| **Frames** and grouping     | Visually group related items                                                                                                                    |
| **Filters**                 | Render focused subsets of a large master diagram (neighborhood, only/without)                                                                   |
| **Dependency** checking     | Verify that all referenced includes and items are consistent                                                                                    |
| **Includes** and reuse      | Split large diagrams across files, share common item definitions via `include`                                                                  |
| **Markdown** embedding      | Embed diagrams directly in Markdown files and generate all images in one pass (`--markdown` mode)                                               |
| **Layout** control          | Horizontal or vertical orientation, placement constraints between items, relaxed constraints on connections                                     |
| **Styling**                 | Background color, graph title suppression, inline Graphviz attributes, reusable attribute aliases                                               |
| Multiple **output formats** | SVG, PNG, PDF, JPG, EPS, and any other format supported by your Graphviz installation (run `dot -Thelp` for the full list), plus raw DOT source |

## Quick start

```bash
pip install data-flow-diagram
```

Create a file `hello.dfd`:

```
entity    User
process   App
store     DB

User --> App    request
App  --> DB     query
DB   --> App    result
App  --> User   response
```

Generate the diagram:

```bash
data-flow-diagram hello.dfd -o hello.svg --no-graph-title
```

You should obtain:

![Quick start result](https://raw.githubusercontent.com/pbauermeister/dfd/main/img/quick-start.svg "Quick start example")

Or pipe directly from stdin:

```bash
echo 'entity User
process App
User --> App  request' | data-flow-diagram -o quick.svg --no-graph-title
```

![Stdin pipe result](https://raw.githubusercontent.com/pbauermeister/dfd/main/img/quick-start-stdin.svg "Stdin pipe example")

## Installing

### For users

Requires Python 3.11+ and [Graphviz](https://graphviz.org/download/).

**Linux (Debian/Ubuntu):**

```bash
sudo apt install graphviz
pip install data-flow-diagram
```

**macOS (Homebrew):**

```bash
brew install graphviz python3
pip install data-flow-diagram
```

If you get a `ModuleNotFoundError: No module named 'reportlab.graphics._renderPM'`
error at runtime, reinstall reportlab:

```bash
pip install --upgrade --force-reinstall reportlab
```

### For developers

Requires GNU Make (pre-installed on most Linux distributions; on macOS, install
the Xcode Command Line Tools if not already present: `xcode-select --install`).

```bash
git clone https://github.com/pbauermeister/dfd.git
cd dfd
make all    # creates venv, installs deps, formats, lints, tests, builds docs
```

`make all` auto-detects your OS and installs the required system packages
(Debian `apt` or macOS `brew`). Run `make help` for all available targets.

## Documentation

Full syntax reference, examples, and advanced features:

<!-- AUTO:doc-toc -->

- [1. Methodology and scope](doc/README.md#1-methodology-and-scope)
- [2. Syntax](doc/README.md#2-syntax)
- [3. Details with examples](doc/README.md#3-details-with-examples)
- [4. Markdown snippets](doc/README.md#4-markdown-snippets)
- [5. Including](doc/README.md#5-including)
- [6. Dependencies](doc/README.md#6-dependencies)
- [7. Filters](doc/README.md#7-filters)
- [8. Influencing the layout](doc/README.md#8-influencing-the-layout)

<!-- /AUTO:doc-toc -->

## Usage

`data-flow-diagram -h` says:

<!-- AUTO:cli-help -->

````
usage: data-flow-diagram [-h] [--output-file OUTPUT_FILE] [--markdown]
                         [--format FORMAT]
                         [--background-color BACKGROUND_COLOR]
                         [--no-graph-title] [--no-check-dependencies]
                         [--debug] [--version]
                         [INPUT_FILE]

Command-line DFD diagram generator. Converts a textual description into a
graphic file.

positional arguments:
  INPUT_FILE            DFD input file; if omitted, stdin is used

options:
  -h, --help            show this help message and exit
  --output-file OUTPUT_FILE, -o OUTPUT_FILE
                        output file name; pass '-' to use stdout; if omitted,
                        use INPUT_FILE base name with '.svg' extension, or
                        stdout
  --markdown, -m        consider snippets between opening marker: ```data-
                        flow-diagram OUTFILE, and closing marker: ``` allowing
                        to generate all diagrams contained in an INPUT_FILE
                        that is a markdown file
  --format FORMAT, -f FORMAT
                        output format: gif, jpg, tiff, bmp, pnm, eps, pdf, svg
                        (any supported by Graphviz), or dot (raw Graphviz DOT
                        text); default is svg
  --background-color BACKGROUND_COLOR, -b BACKGROUND_COLOR
                        background color name (including 'none' for
                        transparent) in web color notation; see
                        https://developer.mozilla.org/en-
                        US/docs/Web/CSS/color_value for a list of valid names;
                        default is white
  --no-graph-title      suppress graph title
  --no-check-dependencies
                        suppress dependencies checking
  --debug               emit debug messages
  --version, -V         print the version and exit

See https://github.com/pbauermeister/dfd for information, syntax and examples.
````

<!-- /AUTO:cli-help -->

## Links

- **Source code:** [github.com/pbauermeister/dfd](https://github.com/pbauermeister/dfd)
- **Package:** [pypi.org/project/data-flow-diagram](https://pypi.org/project/data-flow-diagram/)
- **Changelog:** [CHANGES.md](CHANGES.md)
- **License:** [GPLv3](LICENSE)
