from __future__ import annotations

import re
from pathlib import Path


def test_live_smoke_embedded_python_compiles() -> None:
    script = Path("scripts/smoke-cloud-run.sh").read_text(encoding="utf-8")

    multiline = re.findall(r"python(?:3)? -c '\n(.*?)\n'", script, flags=re.DOTALL)
    assert len(multiline) >= 7
    for index, source in enumerate(multiline, start=1):
        compile(source, f"<smoke-python-multiline-{index}>", "exec")

    single_line = re.findall(r"python(?:3)? -c '([^'\n]+)'", script)
    assert len(single_line) >= 1
    for index, source in enumerate(single_line, start=1):
        compile(source, f"<smoke-python-inline-{index}>", "exec")
