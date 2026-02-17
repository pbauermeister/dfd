```data-flow-diagram tests/non-regression/022-include-snippet/included-snippet-1.dot
process	P3	Process 3
process	P4	Process 4
```

```data-flow-diagram tests/non-regression/022-include-snippet/includer-1.dot
#include #tests/non-regression/022-include-snippet/included-snippet-1

P3 --> P4	connection
```
