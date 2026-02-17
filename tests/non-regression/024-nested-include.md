```data-flow-diagram #tests/non-regression/024-nested-include/snippet-1
process	P1
process	P2
```

```data-flow-diagram #tests/non-regression/024-nested-include/snippet-2
#include #tests/non-regression/024-nested-include/snippet-1
process	P3
```

```data-flow-diagram tests/non-regression/024-nested-include/nested-include.dot
#include #tests/non-regression/024-nested-include/snippet-2

P1 --> P3	connection
P2 --> P3	connection
```
