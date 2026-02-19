"""DFD exception class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .model import pack

if TYPE_CHECKING:
    from .model import SourceLine


class DfdException(Exception):
    def __init__(self, msg: str, source: SourceLine | None = None):
        self.source = source
        self._msg = msg
        self._accumulated: list[tuple[str, SourceLine | None]] = []
        super().__init__(self._format())

    def add(self, msg: str, source: SourceLine | None = None) -> None:
        """Accumulate an additional error with optional source context."""
        self._accumulated.append((msg, source))
        Exception.__init__(self, self._format())

    def __bool__(self) -> bool:
        """True when add() has been called at least once."""
        return len(self._accumulated) > 0

    @staticmethod
    def _mk_prefix(src: SourceLine) -> str:
        """Build an error prefix showing the source location stack."""

        def _add_to_stack(stack: list[str], src: SourceLine) -> None:
            if src.line_nr is None:
                stack += [f"  {pack(src.raw_text)}"]
            else:
                if src.parent and src.parent.is_container:
                    nr = src.parent.line_nr + 1
                    delta = src.line_nr + 1
                    final = nr + delta
                    stack += [f"  line {final}: {pack(src.raw_text)}"]
                else:
                    nr = src.line_nr + 1
                    stack += [f"  line {nr}: {pack(src.raw_text)}"]
            if src.parent:
                _add_to_stack(stack, src.parent)

        stack: list[str] = ["(most recent first)"]
        _add_to_stack(stack, src)
        stack += [""]
        return "\n".join(stack) + "Error: "

    def _format(self) -> str:
        """Format all accumulated errors into a single message."""
        if self.source is not None:
            base = f"{self._mk_prefix(self.source)}{self._msg}"
        else:
            base = self._msg
        if not self._accumulated:
            return base
        parts = [base]
        for msg, src in self._accumulated:
            if src is not None:
                parts.append(f"{self._mk_prefix(src)}{msg}")
            else:
                parts.append(msg)
        return "\n\n".join(parts)
