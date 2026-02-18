# 028 — Fix GH Action Unit Tests

**Date:** 2026-02-18
**Status:** ONGOING

---

## Requirement

GitHub Actions CI fails when running pytest. The error is:

```
ModuleNotFoundError: No module named 'pkg_resources'
```

Traceback origin: `tests/conftest.py:9` imports `data_flow_diagram`, which
causes `src/data_flow_diagram/__init__.py:20` to execute `import pkg_resources`.

`pkg_resources` is provided by `setuptools`, which is not part of the Python
standard library. In Python 3.12+ CI environments it is not guaranteed to be
present, and it is deprecated in favour of `importlib.metadata` (stdlib since
Python 3.8).

---

## Design

**Root cause:** `__init__.py` uses `pkg_resources` solely to read the
installed package version at import time. Three lines are affected:

```python
import pkg_resources                                          # line 20
    VERSION = pkg_resources.require("data-flow-diagram")[0].version  # line 26
except pkg_resources.DistributionNotFound:                    # line 27
```

**Fix:** Replace those three lines with the equivalent `importlib.metadata`
API, which is part of the standard library and requires no external package:

```python
from importlib.metadata import version, PackageNotFoundError
    VERSION = version("data-flow-diagram")
except PackageNotFoundError:
```

No other files in `src/` import `pkg_resources`.

The CI workflow (`ci.yml`) currently installs `setuptools` as a workaround;
that explicit mention of `setuptools` can be removed once the code no longer
needs it, keeping the CI dependency list minimal.

**Scope:** Two files change:
- `src/data_flow_diagram/__init__.py` — swap `pkg_resources` for `importlib.metadata`
- `.github/workflows/ci.yml` — drop the now-unnecessary `setuptools` from the `pip install` line

No behavioural change: `VERSION` is still set to the package version string,
or `"undefined"` when the package is not installed (e.g. during development
without `pip install -e .`).
