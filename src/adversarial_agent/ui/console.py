"""The single shared rich Console used across the app.

On Windows we force UTF-8 output and bypass the legacy-console renderer so that
box-drawing characters (panels, rules) don't crash when output is piped or run
in a non-UTF-8 code page.
"""

from __future__ import annotations

import sys

from rich.console import Console

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass

console = Console(legacy_windows=False)
