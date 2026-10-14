"""
Validate n8n workflow JSON files.

Catches the mistakes that make an import fail or a workflow silently broken:
  - missing required top-level keys
  - node has no id / name / type / position
  - duplicate node names (connections break by name)
  - a connection points to a node that does not exist
  - a node is orphaned (no incoming or outgoing connection)
  - env vars used in the workflow but not declared in meta.requires
  - an HTTP node with no url

    python scripts/validate_workflows.py
    python scripts/validate_workflows.py workflows/*.json

Exit code is non-zero when any file fails, so it works in CI.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REQUIRED_TOP = {"id", "name", "nodes", "connections"}
NODE_REQUIRED = {"id", "name", "type", "position"}
ENV_RE = re.compile(r"\$env\.([A-Z0-9_]+)")


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        wf = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"invalid JSON: {e}"]

    missing = REQUIRED_TOP - set(wf)
    if missing:
        errors.append(f"missing top-level keys: {sorted(missing)}")
        return errors

    nodes = wf["nodes"]
    if not isinstance(nodes, list) or not nodes:
        errors.append("nodes must be a non-empty list")
        return errors

    names = [n.get("name") for n in nodes]
    ids = [n.get("id") for n in nodes]

    for n in nodes:
        miss = NODE_REQUIRED - set(n)
        if miss:
            errors.append(f"node '{n.get('name', '?')}' missing {sorted(miss)}")
        if not isinstance(n.get("position"), list) or len(n.get("position")) != 2:
            errors.append(f"node '{n.get('name', '?')}' has a bad position")
        if n.get("type", "").endswith("httpRequest"):
            params = n.get("parameters", {})
            if not params.get("url"):
                errors.append(f"HTTP node '{n.get('name')}' has no url")

    if len(names) != len(set(names)):
        dup = [x for x in set(names) if names.count(x) > 1]
        errors.append(f"duplicate node names (connections break): {dup}")
    if len(ids) != len(set(ids)):
        errors.append("duplicate node ids")

    known = set(names)
    referenced: set[str] = set()
    for src, outputs in wf["connections"].items():
        if src not in known:
            errors.append(f"connection from unknown node '{src}'")
        for branch in outputs.get("main", []):
            for conn in branch:
                tgt = conn.get("node")
                referenced.add(tgt)
                if tgt not in known:
                    errors.append(f"connection to unknown node '{tgt}'")

    sources = set(wf["connections"].keys())
    for n in nodes:
        name = n["name"]
        if name not in sources and name not in referenced and len(nodes) > 1:
            errors.append(f"orphan node (no connections): '{name}'")

    declared = set(wf.get("meta", {}).get("requires", []))
    for n in nodes:
        blob = json.dumps(n)
        for env in ENV_RE.findall(blob):
            # allow either an exact declared name or a declared prefix (e.g. GROQ_API_KEY)
            if env not in declared and f"{env}_API_KEY" not in declared:
                # look for any declared entry that shares the first token
                root = env.split("_")[0]
                if not any(d.startswith(root) for d in declared):
                    errors.append(
                        f"uses $env.{env} but meta.requires does not declare it")
    return errors


def main(argv: list[str]) -> int:
    args = argv[1:]
    if args:
        files = [Path(a) for a in args]
    else:
        here = Path(__file__).resolve().parent.parent
        files = sorted((here / "workflows").glob("*.json"))

    total_errors = 0
    for f in files:
        errs = validate(f)
        if errs:
            total_errors += len(errs)
            print(f"FAIL  {f.name}")
            for e in errs:
                print(f"      - {e}")
        else:
            print(f"OK    {f.name}")
    print()
    print(f"{len(files)} file(s), {total_errors} error(s)")
    return 1 if total_errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
