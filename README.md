# DFD

DFD (Data Flow Diagram) Generator - Commandline tool to generate
diagrams as images in various formats (SVG, PNG, JPG, PDF, etc.) from
source text files.

The source for this project is [available here][src].
The package page is [available here][pypi].

## Scope

The present tool allows to create diagrams following the "Structured
Analysis / Stuctured Design" (SA/SD) modelling technique as described
by Edward Yourdon.

SA/RT (which is SA/SD with a real-time extension), can be found in the
design of real-time and embedded systems.
Example: [Firmware modelling of the Active Descent
System](https://www.spyr.ch/ps/ads/qm/node18.html) of the [Rosetta
Lander](https://en.wikipedia.org/wiki/Rosetta_(spacecraft))
spacecraft.

Surprisingly, SA/RT is also well-suited to the analyse and design of
web micro-services and IoT architectures.

## Summary
Data Flow Diagram are used to model the flow and processing of
information through a system.

```data-flow-diagram example.svg
process	P	Process
process	P2	Process
entity	E	Entity
store	S	Store
channel	C	Channel

E  --> P	flow
P  ::> P2	signal
P  <-> S	bidirectional flow
P  --- C	undirected flow
```

![simple example](https://raw.githubusercontent.com/pbauermeister/dfd/master/example.svg "Simple example")

## Syntax and examples

See the [documentation page][doc].

## Dependencies

 * Python3
 * Graphviz

## Installing via pip3

```
[sudo] pip3 install data-flow-diagram
```

## Installation troubleshooting

If you get an error at runtime like:
```
ModuleNotFoundError: No module named 'reportlab.graphics._renderPM'
```
you may have to reinstall reportlab:
```
[sudo] python3 -m pip install --upgrade --force-reinstall reportlab
```

## Usage

`data-flow-diagram -h` says:

```
usage: data-flow-diagram [-h] [--output-file OUTPUT_FILE] [--markdown]
                         [--format FORMAT] [--percent-zoom PERCENT_ZOOM]
                         [--background-color BACKGROUND_COLOR] [--debug]
                         [INPUT_FILE]

Command-line DFD diagram generator. Converts a textual description into a
graphic file.

positional arguments:
  INPUT_FILE            UML sequence input file; if omitted, stdin is used

options:
  -h, --help            show this help message and exit
  --output-file OUTPUT_FILE, -o OUTPUT_FILE
                        output file name; pass '-' to use stdout; if
                        omitted, use INPUT_FILE base name with '.svg'
                        extension, or stdout
  --markdown, -m        consider snippets between opening marker:
                        ```data-flow-diagram OUTFILE, and closing marker:
                        ``` allowing to generate all diagrams contained in
                        an INPUT_FILE that is a markdown file
  --format FORMAT, -f FORMAT
                        output format: gif, jpg, tiff, bmp, pnm, eps, pdf,
                        svg (any supported by Graphviz); default is svg
  --no-graph-title      suppress graph title
  --no-check-dependencies
                        suppress dependencies checking
  --debug               emits debug messages

See https://github.com/pbauermeister/dfd for information, syntax and
examples.
```

[src]: https://github.com/pbauermeister/dfd
[pypi]: https://pypi.org/project/data-flow-diagram
[doc]: https://github.com/pbauermeister/dfd/tree/master/doc/README.md
