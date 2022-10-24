# Data Flow Diagram

## Syntax

### Creating items

```data-flow-diagram items.svg
# create a process bubble:
process	P	Do something

# create a terminal rectangle:
entity	T	An entity

# create a store:
store	S	A store

# create a channel
channel	C	A channel
```
![Creating items](./items.svg)

### Creating connections between items

```data-flow-diagram connections.svg
process	A1	A1
process	A2	A2
process	B1	B1
process	B2	B2
process	C1	C1
process	C2	C2
process D	D
process E	E

# create all types of connections:
flow	A1	A2	a flow
bflow	B1	B2	a bi-directional flow
signal	C1	C2	a signal

flow	*	D	an unsourced\nconnection
flow	E	*	an untargetted\nconnection
```
![Creating connections](./connections.svg)

### A simple complete example
```data-flow-diagram complete-example.svg
style	horizontal

process	P	Acquire data
process	P2	Compute
entity	T	Device
store	S	Configuration
channel	C	API

flow	T	P	raw data
flow	P	P2	raw records
signal	*	P	clock
bflow	S	P2	parameters

flow	P2	C  	records
```
![Creating items](./complete-example.svg)
