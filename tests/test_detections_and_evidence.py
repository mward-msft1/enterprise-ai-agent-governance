import csv
import hashlib
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from eagov.apim.policy import load_policy, validate_policy
from eagov.sentinel.rules import load_arm_template

ROOT = Path(__file__).resolve().parents[1]


class DetectionEvidenceTests(unittest.TestCase):
    def test_catalog_queries_use_declared_columns(self):
        catalog = json.loads((ROOT / "detections" / "catalog.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(catalog["detections"]), 9)
        for detection in catalog["detections"]:
            query = (ROOT / detection["query_file"]).read_text(encoding="utf-8")
            self.assertIn(detection["id"], query)
            body = "\n".join(
                line for line in query.splitlines() if not line.strip().startswith("//")
            )
            for column in detection["required_columns"]:
                self.assertIn(column, body, detection["id"])

    def test_arm_rules_are_disabled_by_default(self):
        template = load_arm_template()
        self.assertFalse(template["parameters"]["deployRules"]["defaultValue"])
        self.assertGreaterEqual(len(template["resources"]), 5)
        for resource in template["resources"]:
            self.assertEqual(resource["condition"], "[parameters('deployRules')]")
            self.assertFalse(resource["properties"]["enabled"])
            self.assertIn("TimeGenerated", resource["properties"]["query"])

    def test_evidence_is_labeled_and_hashed(self):
        manifest = json.loads(
            (ROOT / "evidence" / "sample-evidence-manifest.json").read_text(encoding="utf-8")
        )
        self.assertTrue(manifest["not_customer_evidence"])
        self.assertGreaterEqual(len(manifest["items"]), 22)
        for item in manifest["items"]:
            path = ROOT / item["path"]
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["classification"], "SYNTHETIC")
            self.assertTrue(payload["not_customer_evidence"])
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(digest, item["sha256"])

    def test_every_checklist_item_has_a_test_result(self):
        with (ROOT / "checklists" / "tenant-configuration-checklist.csv").open(encoding="utf-8") as handle:
            checklist_ids = {row["Item ID"] for row in csv.DictReader(handle)}
        with (ROOT / "TENANT-TEST-RESULTS.csv").open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        result_ids = {row["Checklist item"] for row in rows}
        self.assertEqual(checklist_ids, result_ids)
        for row in rows:
            self.assertIn("SYNTHETIC", row["Actual result"])
            self.assertIn("tenant validation required", row["Status"])

    def test_apim_policy_requires_jwt_and_has_no_secret(self):
        report = validate_policy(load_policy())
        self.assertTrue(report["valid"], report["missing"])

    def test_json_files_parse(self):
        for path in ROOT.rglob("*.json"):
            if ".venv" in path.parts:
                continue
            json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
