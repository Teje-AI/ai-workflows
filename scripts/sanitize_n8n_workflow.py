#!/usr/bin/env python3
import argparse
import json
import re
import sys
from copy import deepcopy


def slugify(value: str) -> str:
    value = value.strip()
    if not value:
        return "UNKNOWN"
    value = re.sub(r"[^A-Za-z0-9]+", "_", value)
    value = value.strip("_")
    return value.upper() if value else "UNKNOWN"


def sanitize_workflow(data: dict) -> dict:
    data = deepcopy(data)

    # Top-level removals / placeholders
    if "pinData" in data:
        del data["pinData"]
    if "meta" in data:
        del data["meta"]

    if "versionId" in data:
        data["versionId"] = "WORKFLOW_VERSION_ID"
    if "id" in data:
        data["id"] = "WORKFLOW_ID"

    nodes = data.get("nodes")
    if isinstance(nodes, list):
        for idx, node in enumerate(nodes, start=1):
            if not isinstance(node, dict):
                continue

            # Remove credentials anywhere on the node
            if "credentials" in node:
                del node["credentials"]

            # Node id placeholder
            name = node.get("name")
            if "id" in node:
                suffix = slugify(name) if isinstance(name, str) else f"NODE_{idx}"
                node["id"] = f"NODE_ID_{suffix}"

            # Webhook id placeholder
            if "webhookId" in node:
                node["webhookId"] = "WEBHOOK_ID_PLACEHOLDER"

            # Assignment ids placeholder
            params = node.get("parameters")
            if isinstance(params, dict):
                assignments = params.get("assignments")
                if isinstance(assignments, dict):
                    items = assignments.get("assignments")
                    if isinstance(items, list):
                        for a in items:
                            if not isinstance(a, dict):
                                continue
                            if "id" in a:
                                a_name = a.get("name")
                                a_suffix = slugify(a_name) if isinstance(a_name, str) else "ASSIGNMENT"
                                a["id"] = f"ASSIGNMENT_ID_{a_suffix}"

    return data


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sanitize an n8n workflow JSON for public sharing (remove secrets/IDs)."
    )
    parser.add_argument("input", help="Path to the n8n workflow JSON file")
    parser.add_argument("output", nargs="?", help="Optional output path (defaults to stdout)")
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        print(f"Error reading input: {exc}", file=sys.stderr)
        return 2

    sanitized = sanitize_workflow(data)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(sanitized, f, ensure_ascii=False, indent=2)
                f.write("\n")
        except Exception as exc:
            print(f"Error writing output: {exc}", file=sys.stderr)
            return 3
    else:
        json.dump(sanitized, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
