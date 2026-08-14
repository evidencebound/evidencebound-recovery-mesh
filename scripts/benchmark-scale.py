#!/usr/bin/env python3
from __future__ import annotations

import json

from recovery_mesh.scale_probe import run_scale_probe


if __name__ == "__main__":
    print(json.dumps(run_scale_probe().as_dict(), indent=2, sort_keys=True))
