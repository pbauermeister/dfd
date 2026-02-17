```data-flow-diagram tests/non-regression/019-wrapping-with-include/wrapping-1.dot
style vertical

process	P1  Do this and this and also this
process P2  Do\n that and that and also that

P1 -->  P2  result of doing all this
P2 -->  P1  result\nof doing all that
```

```data-flow-diagram tests/non-regression/019-wrapping-with-include/wrapping-2.dot
#include #tests/non-regression/019-wrapping-with-include/wrapping-1
style item-text-width 40
style connection-text-width 40
```

```data-flow-diagram tests/non-regression/019-wrapping-with-include/wrapping-3.dot
#include #tests/non-regression/019-wrapping-with-include/wrapping-1
style item-text-width 8
style connection-text-width 6
```
