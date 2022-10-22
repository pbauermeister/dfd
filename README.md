# DFD

DFD (Data Flow Diagram) Generator - Commandline tool to generate
diagrams as images in various formats (SVG, PNG, JPG, PDF, etc.) from
source text files.

The source for this project is [available here][src].
The package page is [available here][pypi].

## Summary
Data Flow Diagram are used to model the flow and processing of
information through a system.

```data_flow_diagram example.svg
process	P	Process
process	P2	Process
entity	E	Entity
store	S	Store
channel	C	Channel

flow	E	P	flow
signal	P	P2	signal
bflow	P	S	flow
flow	P	C	flow
```

![simple example](https://raw.githubusercontent.com/pbauermeister/dfd/master/example.svg "Simple example")

## Syntax and examples

See the [documentation page][doc].

## Dependencies

 * Python3
 * Python libraries: svgwrite, reportlab

## Installing via pip3

```
[sudo] pip3 install data_flow_diagram
```

## Usage

`data_flow_diagram -h` says:

```
usage: data_flow_diagram [-h]
```

[src]: https://github.com/pbauermeister/dfd
[pypi]: https://pypi.org/project/data-flow-diagram
[doc]: https://github.com/pbauermeister/dfd/tree/master/doc/README.md
