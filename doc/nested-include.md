```data-flow-diagram #snippet-1
process	P1
process	P2
```

```data-flow-diagram #snippet-2
#include #snippet-1
process	P3
```

```data-flow-diagram nested-include.svg
#include #snippet-2

P1 --> P3	connection
P2 --> P3	connection
```
![Nested](./nested-include.svg)
