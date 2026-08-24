from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, cast

import pytest

REPO_ROOT = Path(__file__).parents[2]
ARTIFACT_ROOT = REPO_ROOT / "artifacts" / "1kpapers-company-series"


def _validator_module() -> ModuleType:
    path = REPO_ROOT / "scripts" / "validate_1kpapers_company_series.py"
    spec = importlib.util.spec_from_file_location("company_series_validator", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = _validator_module()


@pytest.fixture
def package(tmp_path: Path) -> Path:
    target = tmp_path / "series"
    shutil.copytree(ARTIFACT_ROOT, target)
    return target


def _json(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _errors(package: Path, *, require_final: bool = False) -> str:
    return "\n".join(VALIDATOR.validate(package, require_final=require_final)["errors"])


def test_real_package_passes() -> None:
    report = VALIDATOR.validate(ARTIFACT_ROOT)
    assert report["ready"] is True, report["errors"]
    assert report["counts"] == {"companies": 3, "drafts": 12, "evidence_bundles": 9}


def test_wrong_company_count_fails(package: Path) -> None:
    shutil.copytree(package / "drafts" / "01-google-deepmind", package / "drafts" / "04-extra")
    assert "draft companies must be exactly" in _errors(package)


def test_fourth_review_fails(package: Path) -> None:
    shutil.copy(
        package / "drafts" / "01-google-deepmind" / "paper-03.md",
        package / "drafts" / "01-google-deepmind" / "paper-04.md",
    )
    assert "expected 12 drafts" in _errors(package)


def test_missing_evidence_fails(package: Path) -> None:
    (package / "evidence" / "02-anthropic" / "paper-03.json").unlink()
    assert "expected 9 evidence bundles" in _errors(package)


def test_duplicate_stable_id_fails(package: Path) -> None:
    path = package / "source-inventory.json"
    data = _json(path)
    candidates = data["candidates"]
    assert isinstance(candidates, list)
    candidates[1]["stable_id"] = candidates[0]["stable_id"]
    _write_json(path, data)
    assert "duplicate stable IDs" in _errors(package)


def test_broken_link_fails(package: Path) -> None:
    path = package / "drafts" / "03-openai" / "index.md"
    path.write_text(
        path.read_text(encoding="utf-8") + "\n[깨진 링크](missing.md)\n",
        encoding="utf-8",
    )
    assert "broken Markdown link" in _errors(package)


def test_missing_apa_fails(package: Path) -> None:
    path = package / "drafts" / "03-openai" / "paper-01.md"
    content = path.read_text(encoding="utf-8").replace("arXiv:", "preprint:")
    path.write_text(content, encoding="utf-8")
    assert "APA arXiv reference missing" in _errors(package)


def test_preflight_warning_fails(package: Path) -> None:
    path = package / "drafts" / "02-anthropic" / "paper-01.md"
    content = path.read_text(encoding="utf-8").replace(
        "**How AI Impacts Skill Formation**",
        "How AI Impacts Skill Formation",
        1,
    )
    path.write_text(content, encoding="utf-8")
    assert "citability warnings" in _errors(package)


def test_published_true_fails(package: Path) -> None:
    path = package / "approval-manifest.json"
    data = _json(path)
    items = data["items"]
    assert isinstance(items, list)
    items[0]["published"] = True
    _write_json(path, data)
    assert "approval and published must be false" in _errors(package)


def test_verifier_and_manifest_pending_fail_final_mode(package: Path) -> None:
    critical_path = package / "reports" / "critical-review.md"
    critical = (
        critical_path.read_text(encoding="utf-8")
        .replace(
            '"finalStatus":"complete"',
            '"finalStatus":"pending"',
        )
        .replace(
            '"agentRole":"verifier","lane":"independent-final-verifier","status":"complete"',
            '"agentRole":"verifier","lane":"independent-final-verifier","status":"pending"',
        )
    )
    critical_path.write_text(critical, encoding="utf-8")
    manifest_path = package / "approval-manifest.json"
    manifest = _json(manifest_path)
    for item in manifest["items"]:
        item["independent_review_status"] = "pending"
        item["revision_status"] = "revised_pending_rereview"
    _write_json(manifest_path, manifest)
    errors = _errors(package, require_final=True)
    assert "critical review lane evidence is incomplete" in errors
    assert "final critical-review gate is incomplete" in errors
    assert "gdm-index: independent final review is not complete" in errors
    assert "openai-03: independent final review is not complete" in errors
    assert "final code-review gate is not APPROVE" not in errors
    assert "final architecture gate is not CLEAR" not in errors


def test_blocking_review_fails_final_mode(package: Path) -> None:
    path = package / "reports" / "code-review.json"
    data = _json(path)
    data["status"] = "complete"
    data["recommendation"] = "BLOCK"
    _write_json(path, data)
    assert "final code-review gate is not APPROVE" in _errors(package, require_final=True)


def test_empty_evidence_fails(package: Path) -> None:
    path = package / "evidence" / "03-openai" / "paper-01.json"
    data = _json(path)
    data["evidence_ledger"] = []
    _write_json(path, data)
    assert "evidence ledger must contain at least three rows" in _errors(package)


def test_unsupported_numeric_claim_fails(package: Path) -> None:
    path = package / "drafts" / "03-openai" / "paper-03.md"
    content = path.read_text(encoding="utf-8").replace(
        "## 해석",
        "확인되지 않은 결과는 987654321%라고 주장한다.\n\n## 해석",
    )
    path.write_text(content, encoding="utf-8")
    assert "unsupported numeric sentences" in _errors(package)


def test_path_traversal_fails(package: Path) -> None:
    path = package / "editorial-map.json"
    data = _json(path)
    entries = data["entries"]
    assert isinstance(entries, list)
    entries[0]["local_path"] = "../outside.md"
    _write_json(path, data)
    assert "local_path escapes artifact root" in _errors(package)


def test_wrong_company_tag_and_duplicate_link_fail(package: Path) -> None:
    path = package / "editorial-map.json"
    data = _json(path)
    entries = data["entries"]
    assert isinstance(entries, list)
    entries[0]["company"] = "OpenAI"
    entries[0]["tags"].append("openai")
    entries[0]["links_to"].append(entries[0]["links_to"][0])
    _write_json(path, data)
    errors = _errors(package)
    assert "company does not match local path" in errors
    assert "duplicate tag or link" in errors


def test_malformed_null_shape_fails_deterministically(package: Path) -> None:
    path = package / "editorial-map.json"
    data = _json(path)
    data["entries"] = None
    _write_json(path, data)
    assert "editorial entries must be a list" in _errors(package)


def test_hostile_discovery_hostname_fails(package: Path) -> None:
    path = package / "source-inventory.json"
    data = _json(path)
    candidates = data["candidates"]
    assert isinstance(candidates, list)
    candidates[0]["discovery_sources"] = ["https://www.1kpapers.com.evil.test/lab"]
    _write_json(path, data)
    assert "discovery URLs must use exact 1kpapers.com hostname" in _errors(package)


def test_attribution_organization_mismatch_fails(package: Path) -> None:
    path = package / "source-inventory.json"
    data = _json(path)
    candidates = data["candidates"]
    assert isinstance(candidates, list)
    candidates[0]["company_attribution"]["organization"] = "Google"
    _write_json(path, data)
    assert "attribution organization must match canonical company" in _errors(package)


def test_null_and_wrong_selection_weights_fail(package: Path) -> None:
    path = package / "source-inventory.json"
    data = _json(path)
    data["selection_weights"] = None
    _write_json(path, data)
    errors = _errors(package)
    assert "selection_weights must be an object" in errors
    assert "score dimensions are invalid" in errors


def test_wrong_weight_and_score_bound_fail(package: Path) -> None:
    path = package / "source-inventory.json"
    data = _json(path)
    data["selection_weights"]["trend"] = 24
    data["candidates"][0]["score_breakdown"]["recency"] = 99
    data["candidates"][0]["selection_score"] += 84
    _write_json(path, data)
    errors = _errors(package)
    assert "score dimensions are invalid" in errors
    assert "outside its PRD bound" in errors


def test_duplicate_title_and_wrong_order_fail(package: Path) -> None:
    path = package / "editorial-map.json"
    data = _json(path)
    data["entries"][1]["title"] = data["entries"][0]["title"]
    data["entries"][1]["order"] = data["entries"][0]["order"]
    _write_json(path, data)
    errors = _errors(package)
    assert "editorial title must be unique" in errors
    assert "orders must be unique and exactly 1..12" in errors


def test_forged_minimal_final_statuses_fail(package: Path) -> None:
    code_path = package / "reports" / "code-review.json"
    code = _json(code_path)
    code["status"] = "complete"
    code["recommendation"] = "APPROVE"
    code["independentReview"] = {"agentRole": "code-reviewer", "status": "complete"}
    _write_json(code_path, code)
    assert "final code-review independent evidence is invalid" in _errors(
        package, require_final=True
    )


def test_missing_architect_evidence_fails_final(package: Path) -> None:
    path = package / "reports" / "architecture-invariant-audit.json"
    data = _json(path)
    data["status"] = "CLEAR"
    data["independentReview"] = {
        "agentRole": "architect",
        "lane": "independent",
        "status": "complete",
        "evidence": "",
    }
    _write_json(path, data)
    assert "final architecture independent evidence is invalid" in _errors(
        package, require_final=True
    )


def test_duplicate_critical_review_lane_fails_final(package: Path) -> None:
    path = package / "reports" / "critical-review.md"
    content = path.read_text(encoding="utf-8").replace(
        '"lane":"independent-final-verifier"',
        '"lane":"independent-editorial-critic-final"',
    )
    content = content.replace('"finalStatus":"pending"', '"finalStatus":"complete"')
    content = content.replace('"status":"pending"', '"status":"complete"')
    path.write_text(content, encoding="utf-8")
    assert "all independent review lane IDs must be globally distinct" in _errors(
        package, require_final=True
    )


def test_null_evidence_ledger_field_fails(package: Path) -> None:
    path = package / "evidence" / "01-google-deepmind" / "paper-01.json"
    data = _json(path)
    data["evidence_ledger"][0]["source_anchor"] = None
    _write_json(path, data)
    assert "evidence ledger fields must be non-empty strings" in _errors(package)


@pytest.mark.parametrize("field", ["confidence", "notes"])
def test_other_null_evidence_fields_fail(package: Path, field: str) -> None:
    path = package / "evidence" / "01-google-deepmind" / "paper-01.json"
    data = _json(path)
    data["evidence_ledger"][0][field] = None
    _write_json(path, data)
    assert "evidence ledger fields must be non-empty strings" in _errors(package)


def test_invalid_critical_disposition_and_status_fail(package: Path) -> None:
    path = package / "reports" / "critical-review.md"
    content = path.read_text(encoding="utf-8").replace(
        '"disposition":"accepted"', '"disposition":"ignored"', 1
    )
    path.write_text(content, encoding="utf-8")
    assert "critical review finding disposition is invalid" in _errors(package)


def test_accepted_critical_finding_requires_revalidation(package: Path) -> None:
    path = package / "reports" / "critical-review.md"
    content = path.read_text(encoding="utf-8").replace(
        '"status":"applied_and_reverified"', '"status":"pending"', 1
    )
    path.write_text(content, encoding="utf-8")
    assert "accepted critical finding is not applied and reverified" in _errors(package)


def test_global_duplicate_lane_fails_final(package: Path) -> None:
    code_path = package / "reports" / "code-review.json"
    architecture_path = package / "reports" / "architecture-invariant-audit.json"
    code = _json(code_path)
    architecture = _json(architecture_path)
    architecture["independentReview"]["lane"] = code["independentReview"]["lane"]
    _write_json(architecture_path, architecture)
    assert "lane IDs must be globally distinct" in _errors(package, require_final=True)


def test_mixed_case_self_review_lane_fails_final(package: Path) -> None:
    path = package / "reports" / "code-review.json"
    data = _json(path)
    data["independentReview"]["lane"] = "Independent-Implementation-Owner-SeLf-ReView"
    _write_json(path, data)
    assert "independent reviewer cannot use a self-review lane" in _errors(
        package, require_final=True
    )


def test_untraced_qualitative_claim_marker_fails(package: Path) -> None:
    path = package / "drafts" / "03-openai" / "paper-01.md"
    content = path.read_text(encoding="utf-8").replace(
        "## 해석\n",
        "## 해석\n\n<!-- claim:not-in-ledger -->\n근거 없는 정성 주장을 추가한다.\n",
    )
    path.write_text(content, encoding="utf-8")
    assert "qualitative claim marker is not in evidence ledger" in _errors(package)


def test_rejected_candidate_cannot_use_zero_scores(package: Path) -> None:
    path = package / "source-inventory.json"
    data = _json(path)
    candidate = next(item for item in data["candidates"] if not item["selected"])
    candidate["score_breakdown"]["significance"] = 0
    candidate["selection_score"] = sum(candidate["score_breakdown"].values())
    _write_json(path, data)
    assert "score must use declared discrete bands" in _errors(package)


def test_selected_candidates_must_match_ranked_top_three(package: Path) -> None:
    path = package / "source-inventory.json"
    data = _json(path)
    company = [item for item in data["candidates"] if item["company"] == "Anthropic"]
    selected = next(item for item in company if item["selected"])
    rejected = next(item for item in company if not item["selected"])
    selected["selected"] = False
    selected["editorial_slot"] = None
    selected["exclusion_reason"] = "test replacement"
    rejected["selected"] = True
    rejected["canonical_company"] = "Anthropic"
    rejected["company_attribution_status"] = "verified"
    rejected["exclusion_reason"] = None
    rejected["editorial_slot"] = "human-skill"
    _write_json(path, data)
    assert "selected candidates do not match deterministic ranking" in _errors(package)


def test_manifest_null_item_cli_writes_deterministic_report(package: Path, tmp_path: Path) -> None:
    manifest_path = package / "approval-manifest.json"
    manifest = _json(manifest_path)
    manifest["items"][0] = None
    _write_json(manifest_path, manifest)
    report_path = tmp_path / "report.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "validate_1kpapers_company_series.py"),
            "--root",
            str(package),
            "--report",
            str(report_path),
            "--mode",
            "pre-review",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode != 0
    report = _json(report_path)
    assert "approval manifest item must be an object" in "\n".join(report["errors"])
