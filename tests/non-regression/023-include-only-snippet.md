```data-flow-diagram #tests/non-regression/023-include-only-snippet/includee-snippet-2
process	P5	Process 5
process	P6	Process 6
```

```data-flow-diagram tests/non-regression/023-include-only-snippet/includer-2.dot

#include #tests/non-regression/023-include-only-snippet/includee-snippet-2

P5 --> P6	connection
```
