```data-flow-diagram tests/non-regression/025-dependencies-snippet/Feature-1.dot
process	This    Do this
```

```data-flow-diagram tests/non-regression/025-dependencies-snippet/Referrer-1.dot
# Externals:
none #tests/non-regression/025-dependencies-snippet/Feature-1:

# Internals:
process	That    Do that

tests/non-regression/025-dependencies-snippet/Feature-1 --> That
```

```data-flow-diagram tests/non-regression/025-dependencies-snippet/Referrer-2.dot
# Externals:
process #tests/non-regression/025-dependencies-snippet/Feature-1:This

# Internals:
process	That    Do that

This --> That
```

```data-flow-diagram tests/non-regression/025-dependencies-snippet/Referrer-3.dot
# Externals:
process #tests/non-regression/025-dependencies-snippet/Feature-1:This Do this

# Internals:
process	That    Do that

This --> That
```
