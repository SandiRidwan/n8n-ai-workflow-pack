"""
Tests for the workflow validator — the validator must actually catch problems.

Run:  python -m pytest scripts tests -q   (or)  python tests/test_validator.py
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from validate_workflows import validate  # noqa: E402


def _wf(**over) -> dict:
    base = {
        "id": "t1",
        "name": "test",
        "nodes": [
            {"id": "a", "name": "A", "type": "n8n-nodes-base.code",
             "typeVersion": 2, "position": [0, 0], "parameters": {}},
            {"id": "b", "name": "B", "type": "n8n-nodes-base.code",
             "typeVersion": 2, "position": [200, 0], "parameters": {}},
        ],
        "connections": {"A": {"main": [[{"node": "B", "type": "main", "index": 0}]]}},
        "meta": {"requires": []},
    }
    base.update(over)
    return base


class TestValidator(unittest.TestCase):
    def _write(self, wf: dict) -> Path:
        p = ROOT / "tests" / "_tmp_wf.json"
        p.write_text(json.dumps(wf), encoding="utf-8")
        return p

    def test_valid_passes(self):
        self.assertEqual(validate(self._write(_wf())), [])

    def test_missing_top_key(self):
        wf = _wf()
        del wf["id"]
        self.assertTrue(any("missing top-level" in e
                            for e in validate(self._write(wf))))

    def test_duplicate_node_names(self):
        wf = _wf()
        wf["nodes"][1]["name"] = "A"
        self.assertTrue(any("duplicate node names" in e
                            for e in validate(self._write(wf))))

    def test_connection_to_unknown_node(self):
        wf = _wf()
        wf["connections"] = {"A": {"main": [[{"node": "Ghost",
                                              "type": "main", "index": 0}]]}}
        self.assertTrue(any("unknown node 'Ghost'" in e
                            for e in validate(self._write(wf))))

    def test_orphan_node_detected(self):
        wf = _wf()
        wf["nodes"].append({"id": "c", "name": "C",
                            "type": "n8n-nodes-base.code", "typeVersion": 2,
                            "position": [400, 0], "parameters": {}})
        self.assertTrue(any("orphan node" in e
                            for e in validate(self._write(wf))))

    def test_http_node_without_url(self):
        wf = _wf()
        wf["nodes"][0]["type"] = "n8n-nodes-base.httpRequest"
        wf["nodes"][0]["parameters"] = {}
        self.assertTrue(any("has no url" in e
                            for e in validate(self._write(wf))))

    def test_undeclared_env_flagged(self):
        wf = _wf()
        wf["nodes"][0]["parameters"] = {"url": "https://x", "note": "={{$env.SECRET_TOKEN}}"}
        wf["nodes"][0]["type"] = "n8n-nodes-base.httpRequest"
        errs = validate(self._write(wf))
        self.assertTrue(any("SECRET_TOKEN" in e for e in errs))

    def test_declared_env_ok(self):
        wf = _wf()
        wf["nodes"][0]["type"] = "n8n-nodes-base.httpRequest"
        wf["nodes"][0]["parameters"] = {"url": "https://x", "note": "={{$env.FOO_KEY}}"}
        wf["meta"] = {"requires": ["FOO_KEY"]}
        self.assertEqual(validate(self._write(wf)), [])

    def test_real_workflows_pass(self):
        for f in (ROOT / "workflows").glob("*.json"):
            self.assertEqual(validate(f), [], f"{f.name} should be valid")


if __name__ == "__main__":
    unittest.main(verbosity=2)
