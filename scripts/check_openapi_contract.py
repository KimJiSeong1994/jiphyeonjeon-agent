"""Validate an OpenAPI JSON file against the operations consumed by the MCP adapter."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, cast

from jiphyeonjeon_mcp.openapi_contract import validate_openapi_contract


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("openapi_file", type=Path)
    args = parser.parse_args()
    document = cast(dict[str, Any], json.loads(args.openapi_file.read_text(encoding="utf-8")))
    errors = validate_openapi_contract(document)
    if errors:
        print("OpenAPI contract drift detected:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("OpenAPI contract compatible")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
