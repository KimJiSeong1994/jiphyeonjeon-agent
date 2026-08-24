#!/usr/bin/env python3
"""Validate the local-only 1K Papers company-series editorial package."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from jiphyeonjeon_mcp.tools.blog import _citability_warnings

COMPANY_DIRS = (
    "01-google-deepmind",
    "02-anthropic",
    "03-openai",
)
COMPANY_TAGS = {"google-deepmind", "anthropic", "openai"}
COMMON_TAGS = {"1kpapers-company-series", "company-research", "paper-review"}
REQUIRED_REPORTS = {
    "preflight-report.json",
    "code-review.json",
    "architecture-invariant-audit.json",
    "critical-review.md",
    "verification-report.md",
}
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
NUMBER_RE = re.compile(r"(?<![A-Za-z])(?:\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)(?:km|[kKmMbB×%]|m)?")
SCORE_DIMENSIONS = {
    "trend",
    "recency",
    "significance",
    "thematic_coherence",
    "primary_evidence_availability",
}
EXPECTED_WEIGHTS = {
    "trend": 25,
    "recency": 15,
    "significance": 25,
    "thematic_coherence": 20,
    "primary_evidence_availability": 15,
}
COMPANY_BY_DIR = {
    "01-google-deepmind": ("Google DeepMind", "google-deepmind"),
    "02-anthropic": ("Anthropic", "anthropic"),
    "03-openai": ("OpenAI", "openai"),
}
ALLOWED_AUTHORITATIVE_HOSTS = {
    "arxiv.org",
    "deepmind.google",
    "loger-project.github.io",
    "www.anthropic.com",
    "anthropic.com",
    "openai.com",
    "www.openai.com",
    "evals.openai.com",
    "www.research.google",
    "research.google",
}


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid JSON {path}: {exc}")
        return None


def _required(mapping: dict[str, Any], fields: set[str], label: str, errors: list[str]) -> None:
    missing = sorted(field for field in fields if field not in mapping or mapping[field] == "")
    if missing:
        errors.append(f"{label}: missing required fields {missing}")


def _is_timezone_iso(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _hostname(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.hostname:
        return None
    return parsed.hostname.lower().rstrip(".")


def _confined_path(root: Path, relative: object) -> Path | None:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        return None
    target = (root / relative).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError:
        return None
    return target


def _frontmatter(content: str) -> tuple[dict[str, str], str]:
    if not content.startswith("---\n"):
        return {}, content
    end = content.find("\n---\n", 4)
    if end == -1:
        return {}, content
    metadata: dict[str, str] = {}
    for line in content[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()
    return metadata, content[end + 5 :]


def _claim_ids(value: str | None) -> set[str]:
    if value is None or not value.startswith("[") or not value.endswith("]"):
        return set()
    return {item.strip() for item in value[1:-1].split(",") if item.strip()}


def _validate_structure(root: Path, errors: list[str]) -> tuple[list[Path], list[Path]]:
    drafts_root = root / "drafts"
    evidence_root = root / "evidence"
    draft_dirs = sorted(path.name for path in drafts_root.iterdir() if path.is_dir())
    evidence_dirs = sorted(path.name for path in evidence_root.iterdir() if path.is_dir())
    if draft_dirs != sorted(COMPANY_DIRS):
        errors.append(f"draft companies must be exactly {list(COMPANY_DIRS)}")
    if evidence_dirs != sorted(COMPANY_DIRS):
        errors.append(f"evidence companies must be exactly {list(COMPANY_DIRS)}")

    drafts = sorted(drafts_root.glob("*/*.md"))
    evidence = sorted(evidence_root.glob("*/*.json"))
    if len(drafts) != 12:
        errors.append(f"expected 12 drafts, found {len(drafts)}")
    if len(evidence) != 9:
        errors.append(f"expected 9 evidence bundles, found {len(evidence)}")
    for company in COMPANY_DIRS:
        names = sorted(path.name for path in (drafts_root / company).glob("*.md"))
        if names != ["index.md", "paper-01.md", "paper-02.md", "paper-03.md"]:
            errors.append(f"{company}: expected index.md and exactly three paper drafts")
        evidence_names = sorted(path.name for path in (evidence_root / company).glob("*.json"))
        if evidence_names != ["paper-01.json", "paper-02.json", "paper-03.json"]:
            errors.append(f"{company}: expected exactly three evidence bundles")
    report_names = {path.name for path in (root / "reports").iterdir() if path.is_file()}
    missing_reports = sorted(REQUIRED_REPORTS - report_names)
    if missing_reports:
        errors.append(f"missing reports: {missing_reports}")
    return drafts, evidence


def _validate_inventory(root: Path, errors: list[str]) -> dict[str, dict[str, Any]]:
    data = _load_json(root / "source-inventory.json", errors)
    if not isinstance(data, dict) or not isinstance(data.get("candidates"), list):
        errors.append("source inventory must contain candidates")
        return {}
    weights = data.get("selection_weights")
    if not isinstance(weights, dict):
        errors.append("source inventory selection_weights must be an object")
        weights = {}
    if weights != EXPECTED_WEIGHTS:
        errors.append("source inventory score dimensions are invalid")
    score_contract = data.get("score_evidence_contract")
    if (
        not isinstance(score_contract, dict)
        or set(score_contract) != SCORE_DIMENSIONS
        or not all(isinstance(value, str) and value for value in score_contract.values())
    ):
        errors.append("source inventory score evidence contract is invalid")
    if not isinstance(data.get("trend_observation"), str):
        errors.append("source inventory needs a reproducible trend observation")
    expected_thresholds = {
        "significance_min": 20,
        "thematic_coherence_min": 16,
        "primary_evidence_availability_required": 15,
        "slots_per_company": 3,
    }
    if data.get("selection_thresholds") != expected_thresholds:
        errors.append("source inventory selection thresholds are invalid")
    formula = data.get("score_formula")
    if not isinstance(formula, dict) or {
        key: value for key, value in formula.items() if key != "total"
    } != {
        "trend": {"catalog_present": 25},
        "recency": {"published_2026": 15, "published_2025": 10},
        "significance": {"series_anchor": 25, "strong_adjacent": 20, "eligible": 15},
        "thematic_coherence": {
            "unique_fixed_slot": 20,
            "adjacent_or_redundant": 15,
            "outside_sequence": 10,
        },
        "primary_evidence_availability": {
            "full_bundle_and_direct_attribution": 15,
            "stable_primary_identity": 10,
            "identity_resolution_failed": 5,
        },
    }:
        errors.append("source inventory score formula is invalid")
    if not isinstance(data.get("selection_rule"), str) or not data.get("selection_rule"):
        errors.append("source inventory selection rule is missing")
    pool = data.get("candidate_pool")
    if not isinstance(pool, dict) or pool.get("mode") != "deterministic_filtered_pool":
        errors.append("source inventory candidate pool must be deterministic")
        pool_companies: dict[str, Any] = {}
    else:
        raw_pool_companies = pool.get("companies")
        pool_companies = raw_pool_companies if isinstance(raw_pool_companies, dict) else {}
    candidates: dict[str, dict[str, Any]] = {}
    stable_keys: list[tuple[object, object]] = []
    selected_counts: Counter[str] = Counter()
    fields = {
        "candidate_id",
        "title",
        "stable_id_type",
        "stable_id",
        "primary_url",
        "company",
        "company_attribution_status",
        "company_attribution",
        "company_attribution_rationale",
        "company_attribution_sources",
        "discovery_sources",
        "retrieved_at",
        "trend_evidence",
        "selection_score",
        "score_breakdown",
        "selected",
        "canonical_company",
        "cross_company_affiliations",
        "duplicate_of",
        "evidence_availability",
        "exclusion_reason",
        "score_rationale",
    }
    for raw in data["candidates"]:
        if not isinstance(raw, dict):
            errors.append("inventory candidate must be an object")
            continue
        label = f"candidate {raw.get('candidate_id', '<unknown>')}"
        _required(raw, fields, label, errors)
        candidate_id = raw.get("candidate_id")
        if isinstance(candidate_id, str):
            candidates[candidate_id] = raw
        stable_id_type = raw.get("stable_id_type")
        stable_id = raw.get("stable_id")
        if not isinstance(stable_id_type, str) or not isinstance(stable_id, str):
            errors.append(f"{label}: stable ID must be typed strings")
        stable_keys.append((stable_id_type, stable_id))
        if _hostname(raw.get("primary_url")) != "arxiv.org":
            errors.append(f"{label}: primary URL must use exact arxiv.org hostname")
        if not _is_timezone_iso(raw.get("retrieved_at")):
            errors.append(f"{label}: retrieved_at must be timezone-aware ISO-8601")
        breakdown = raw.get("score_breakdown")
        score = raw.get("selection_score")
        if not isinstance(breakdown, dict) or set(breakdown) != SCORE_DIMENSIONS:
            errors.append(f"{label}: score breakdown dimensions are invalid")
        elif not all(type(value) is int for value in breakdown.values()) or type(score) is not int:
            errors.append(f"{label}: score fields must be integers")
        elif sum(breakdown.values()) != score:
            errors.append(f"{label}: selection score does not equal breakdown sum")
        elif any(
            value < 0 or value > EXPECTED_WEIGHTS[dimension]
            for dimension, value in breakdown.items()
        ):
            errors.append(f"{label}: score dimension is outside its PRD bound")
        if isinstance(breakdown, dict) and breakdown.get("trend") != 25:
            errors.append(f"{label}: catalog-presence trend score must be the binary value 25")
        allowed_bands = {
            "trend": {25},
            "recency": {10, 15},
            "significance": {15, 20, 25},
            "thematic_coherence": {10, 15, 20},
            "primary_evidence_availability": {5, 10, 15},
        }
        if isinstance(breakdown, dict) and any(
            breakdown.get(dimension) not in bands for dimension, bands in allowed_bands.items()
        ):
            errors.append(f"{label}: score must use declared discrete bands")
        rationale = raw.get("score_rationale")
        rationale_fields = {
            "recency",
            "significance",
            "thematic_coherence",
            "primary_evidence_availability",
        }
        if (
            not isinstance(rationale, dict)
            or set(rationale) != rationale_fields
            or any(
                not isinstance(rationale.get(field), str) or not rationale.get(field)
                for field in rationale_fields
            )
        ):
            errors.append(f"{label}: candidate-specific score rationale is invalid")
        elif isinstance(breakdown, dict) and any(
            f"{field}={breakdown.get(field)}" not in str(rationale.get(field))
            for field in rationale_fields
        ):
            errors.append(f"{label}: score rationale does not explain its exact band")
        discovery = raw.get("discovery_sources")
        if not isinstance(discovery, list) or not all(
            _hostname(url) in {"1kpapers.com", "www.1kpapers.com"} for url in discovery
        ):
            errors.append(f"{label}: discovery URLs must use exact 1kpapers.com hostname")
        sources = raw.get("company_attribution_sources")
        if (
            not isinstance(sources, list)
            or not sources
            or not all(_hostname(url) in ALLOWED_AUTHORITATIVE_HOSTS for url in sources)
        ):
            errors.append(f"{label}: attribution sources must use authoritative hostnames")
        attribution = raw.get("company_attribution")
        if not isinstance(attribution, dict):
            errors.append(f"{label}: company attribution must be an object")
            attribution = {}
        organization = attribution.get("organization")
        organization_type = attribution.get("organization_type")
        if not isinstance(organization, str) or not isinstance(organization_type, str):
            errors.append(f"{label}: attribution organization and type must be strings")
        if raw.get("selected") is True:
            selected_counts[str(raw.get("company"))] += 1
            if raw.get("company_attribution_status") != "verified":
                errors.append(f"{label}: selected attribution must be verified")
            if organization != raw.get("company") or organization_type != "company":
                errors.append(f"{label}: attribution organization must match canonical company")
            if raw.get("canonical_company") != raw.get("company"):
                errors.append(f"{label}: canonical company must match selected company")
            if raw.get("exclusion_reason") is not None:
                errors.append(f"{label}: selected item cannot have an exclusion reason")
            if isinstance(breakdown, dict) and (
                breakdown.get("significance", 0) < 20
                or breakdown.get("thematic_coherence", 0) < 16
                or breakdown.get("primary_evidence_availability") != 15
            ):
                errors.append(f"{label}: selected item does not meet rubric thresholds")
        elif not isinstance(raw.get("exclusion_reason"), str) or not raw.get("exclusion_reason"):
            errors.append(f"{label}: non-selected candidate needs an exclusion reason")
    duplicates = [key for key, count in Counter(stable_keys).items() if count > 1]
    if duplicates:
        errors.append(f"duplicate stable IDs: {duplicates}")
    expected = {"Google DeepMind": 3, "Anthropic": 3, "OpenAI": 3}
    if dict(selected_counts) != expected:
        errors.append(f"selected counts must be {expected}, found {dict(selected_counts)}")
    expected_pool_counts = {"Google DeepMind": 11, "Anthropic": 5, "OpenAI": 7}
    actual_pool_counts = Counter(str(item.get("company")) for item in data["candidates"])
    if dict(actual_pool_counts) != expected_pool_counts:
        errors.append(
            "candidate pool counts must be "
            f"{expected_pool_counts}, found {dict(actual_pool_counts)}"
        )
    inventory_ids = {
        company: {
            str(item.get("stable_id"))
            for item in data["candidates"]
            if item.get("company") == company
        }
        for company in expected_pool_counts
    }
    normalized_pool_ids = {
        company: set(ids) if isinstance(ids, list) else set()
        for company, ids in pool_companies.items()
    }
    if inventory_ids != normalized_pool_ids:
        errors.append("candidate pool stable IDs do not match the retrieved catalog declaration")
    expected_slots = {
        "Google DeepMind": {"long-context-geometry", "latent-representation", "video-capability"},
        "Anthropic": {"human-skill", "operational-defense", "data-poisoning"},
        "OpenAI": {"instruction-hierarchy", "economic-evaluation", "hallucination-mechanism"},
    }
    for company, slots in expected_slots.items():
        company_candidates = [item for item in data["candidates"] if item.get("company") == company]
        ranked = sorted(
            company_candidates,
            key=lambda item: (-int(item.get("selection_score", -1)), str(item.get("stable_id"))),
        )
        selected_ids = {
            str(item.get("stable_id")) for item in company_candidates if item.get("selected")
        }
        if selected_ids != {str(item.get("stable_id")) for item in ranked[:3]}:
            errors.append(f"{company}: selected candidates do not match deterministic ranking")
        selected_slots = {
            item.get("editorial_slot") for item in company_candidates if item.get("selected")
        }
        if selected_slots != slots:
            errors.append(f"{company}: selected editorial slots are invalid")
        if any(
            item.get("editorial_slot") is not None
            for item in company_candidates
            if not item.get("selected")
        ):
            errors.append(f"{company}: rejected candidate cannot occupy an editorial slot")
    return candidates


def _validate_editorial(root: Path, errors: list[str]) -> dict[str, dict[str, Any]]:
    data = _load_json(root / "editorial-map.json", errors)
    if not isinstance(data, dict):
        return {}
    if data.get("series_id") != "1kpapers-company-series-2026-pilot":
        errors.append("editorial series_id is invalid")
    if data.get("companies") != list(COMPANY_DIRS):
        errors.append("editorial company order is invalid")
    entries = data.get("entries")
    if not isinstance(entries, list):
        errors.append("editorial entries must be a list")
        return {}
    mapped: dict[str, dict[str, Any]] = {}
    slugs: set[str] = set()
    local_paths: set[str] = set()
    titles: set[str] = set()
    orders: list[int] = []
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("editorial entry must be an object")
            continue
        _required(
            entry,
            {
                "entry_id",
                "company",
                "entry_kind",
                "local_path",
                "proposed_slug",
                "title",
                "order",
                "tags",
                "links_to",
            },
            "editorial entry",
            errors,
        )
        entry_id = str(entry.get("entry_id"))
        if entry_id in mapped:
            errors.append(f"duplicate editorial entry ID: {entry_id}")
        mapped[entry_id] = entry
        slug = str(entry.get("proposed_slug"))
        local_path = str(entry.get("local_path"))
        title = entry.get("title")
        order = entry.get("order")
        if not isinstance(title, str) or not title:
            errors.append(f"{entry_id}: title must be a non-empty string")
        elif title in titles:
            errors.append(f"{entry_id}: editorial title must be unique")
        else:
            titles.add(title)
        if type(order) is not int:
            errors.append(f"{entry_id}: order must be an integer")
        else:
            orders.append(order)
        if slug in slugs or local_path in local_paths:
            errors.append(f"duplicate editorial slug or path: {entry_id}")
        slugs.add(slug)
        local_paths.add(local_path)
        raw_tags = entry.get("tags")
        raw_links = entry.get("links_to")
        if not isinstance(raw_tags, list) or not all(isinstance(tag, str) for tag in raw_tags):
            errors.append(f"{entry_id}: tags must be a string list")
            raw_tags = []
        if not isinstance(raw_links, list) or not all(isinstance(link, str) for link in raw_links):
            errors.append(f"{entry_id}: links_to must be a string list")
            raw_links = []
        if len(raw_tags) != len(set(raw_tags)) or len(raw_links) != len(set(raw_links)):
            errors.append(f"{entry_id}: duplicate tag or link")
        tags = set(raw_tags)
        if not COMMON_TAGS <= tags:
            errors.append(f"{entry_id}: missing common tags")
        if len(tags & COMPANY_TAGS) != 1:
            errors.append(f"{entry_id}: must contain exactly one company tag")
        target = _confined_path(root, local_path)
        if target is None:
            errors.append(f"{entry_id}: local_path escapes artifact root")
            continue
        if not target.is_file():
            errors.append(f"{entry_id}: local_path does not exist")
        company_dir = target.parent.name
        expected_company = COMPANY_BY_DIR.get(company_dir)
        if expected_company is None or entry.get("company") != expected_company[0]:
            errors.append(f"{entry_id}: company does not match local path")
        elif tags & COMPANY_TAGS != {expected_company[1]}:
            errors.append(f"{entry_id}: company tag does not match local path")
        for link in raw_links:
            link_target = _confined_path(root, str(Path(local_path).parent / link))
            if link_target is None or link_target.parent != target.parent:
                errors.append(f"{entry_id}: link escapes sibling directory {link}")
            elif not link_target.is_file():
                errors.append(f"{entry_id}: broken links_to target {link}")
    if len(entries) != 12:
        errors.append(f"editorial map must contain 12 entries, found {len(entries)}")
    if sorted(orders) != list(range(1, 13)):
        errors.append("editorial orders must be unique and exactly 1..12")
    for company in COMPANY_DIRS:
        company_entries = [
            entry
            for entry in entries
            if str(entry.get("local_path", "")).startswith(f"drafts/{company}/")
        ]
        kinds = Counter(str(entry.get("entry_kind")) for entry in company_entries)
        if kinds != {"company_index": 1, "paper_review": 3}:
            errors.append(f"{company}: editorial kinds invalid: {dict(kinds)}")
        for entry in company_entries:
            own_name = Path(str(entry.get("local_path"))).name
            sibling_names = {Path(str(item.get("local_path"))).name for item in company_entries}
            expected_links = sibling_names - {own_name}
            if set(entry.get("links_to", [])) != expected_links:
                errors.append(f"{entry.get('entry_id')}: sibling graph is invalid")
            if entry.get("entry_kind") == "company_index" and "company-index" not in entry.get(
                "tags", []
            ):
                errors.append(f"{entry.get('entry_id')}: company index tag missing")
    return mapped


def _validate_drafts(
    root: Path,
    drafts: list[Path],
    editorial: dict[str, dict[str, Any]],
    errors: list[str],
) -> int:
    ready = 0
    forbidden = ("TODO", "placeholder", "allow_citability_warnings", "## 리뷰어 추가 비판")
    for path in drafts:
        content = path.read_text(encoding="utf-8")
        metadata, body = _frontmatter(content)
        warnings = _citability_warnings(body, "paper-review")
        if warnings:
            errors.append(f"{path}: citability warnings: {warnings}")
        else:
            ready += 1
        if "## References" not in content:
            errors.append(f"{path}: References section missing")
        if any(marker in content for marker in forbidden):
            errors.append(f"{path}: forbidden placeholder/override/reviewer section")
        local_links: list[str] = []
        for target in LINK_RE.findall(body):
            if target.startswith(("https://", "http://", "#")):
                continue
            local_links.append(target)
            resolved = _confined_path(root, str(path.relative_to(root).parent / target))
            if resolved is None or resolved.parent != path.parent.resolve():
                errors.append(f"{path}: Markdown link escapes sibling directory {target}")
            elif not resolved.is_file():
                errors.append(f"{path}: broken Markdown link {target}")
        entry = next(
            (
                value
                for value in editorial.values()
                if value.get("local_path") == str(path.relative_to(root))
            ),
            None,
        )
        if entry is not None and set(local_links) != set(entry.get("links_to", [])):
            errors.append(f"{path}: Markdown links do not match editorial links_to")
        if path.name.startswith("paper-"):
            if metadata.get("review_mode") != "deep_academic_review":
                errors.append(f"{path}: review_mode must be deep_academic_review")
            if not metadata.get("paper_id", "").startswith("arxiv:"):
                errors.append(f"{path}: machine-readable paper_id is missing")
            if not _claim_ids(metadata.get("claim_ids")):
                errors.append(f"{path}: machine-readable claim_ids are missing")
            required_sections = {
                "## Executive Summary",
                "## 방법",
                "## 실험 설정과 결과",
                "## 해석",
                "## 한계와 외적 타당성",
                "## 회사·공동연구 provenance",
                "## References",
            }
            missing_sections = sorted(
                section for section in required_sections if section not in body
            )
            if missing_sections:
                errors.append(f"{path}: missing deep-review sections {missing_sections}")
            tldr_match = re.search(r"\*\*TL;DR\*\*\s*—\s*(.+)", body)
            if tldr_match is None:
                errors.append(f"{path}: TL;DR body is missing")
            else:
                sentences = [
                    item for item in re.split(r"(?<=[.!?])\s+", tldr_match.group(1)) if item
                ]
                if len(sentences) != 3:
                    errors.append(f"{path}: TL;DR must contain exactly three sentences")
                if not any(NUMBER_RE.search(item) or "보고" in item for item in sentences):
                    errors.append(f"{path}: TL;DR needs a headline result")
            references = content.split("## References", 1)[-1]
            if "arXiv:" not in references or "https://arxiv.org/abs/" not in references:
                errors.append(f"{path}: APA arXiv reference missing")
    return ready


def _validate_evidence(
    root: Path,
    evidence_paths: list[Path],
    candidates: dict[str, dict[str, Any]],
    errors: list[str],
) -> None:
    for path in evidence_paths:
        data = _load_json(path, errors)
        if not isinstance(data, dict):
            continue
        _required(
            data,
            {
                "paper",
                "evidence_ledger",
                "method_map",
                "result_table",
                "critique_log",
                "apa_references",
            },
            str(path),
            errors,
        )
        paper = data.get("paper", {})
        if not isinstance(paper, dict):
            errors.append(f"{path}: paper metadata must be an object")
            continue
        _required(
            paper,
            {
                "candidate_id",
                "title",
                "authors",
                "year",
                "version",
                "date",
                "venue",
                "arxiv_id",
                "primary_url",
            },
            str(path),
            errors,
        )
        candidate = candidates.get(str(paper.get("candidate_id")))
        if candidate is None or candidate.get("stable_id") != paper.get("arxiv_id"):
            errors.append(f"{path}: paper ID does not match source inventory")
        draft = root / "drafts" / path.parent.name / f"{path.stem}.md"
        content = draft.read_text(encoding="utf-8") if draft.is_file() else ""
        metadata, body = _frontmatter(content)
        expected_paper_id = f"arxiv:{paper.get('arxiv_id')}"
        if metadata.get("paper_id") != expected_paper_id:
            errors.append(f"{path}: evidence and draft paper IDs differ")
        ledger = data.get("evidence_ledger")
        methods = data.get("method_map")
        results = data.get("result_table")
        critiques = data.get("critique_log")
        references = data.get("apa_references")
        if not isinstance(ledger, list) or len(ledger) < 3:
            errors.append(f"{path}: evidence ledger must contain at least three rows")
            ledger = []
        if not isinstance(methods, list) or len(methods) < 2:
            errors.append(f"{path}: method map must contain at least two rows")
            methods = []
        if not isinstance(results, list) or len(results) < 2:
            errors.append(f"{path}: result table must contain at least two rows")
            results = []
        if not isinstance(critiques, list) or not critiques:
            errors.append(f"{path}: critique log must be a non-empty list")
            critiques = []
        if (
            not isinstance(references, list)
            or not references
            or not all(isinstance(item, str) and item for item in references)
        ):
            errors.append(f"{path}: APA references must be a non-empty string list")
        ledger_ids: list[str] = []
        for claim in ledger:
            if not isinstance(claim, dict):
                errors.append(f"{path}: evidence claim must be an object")
                continue
            _required(
                claim,
                {
                    "claim_id",
                    "final_draft_section",
                    "exact_claim_text",
                    "source_anchor",
                    "evidence_type",
                    "confidence",
                    "notes",
                },
                str(path),
                errors,
            )
            ledger_fields = {
                "claim_id",
                "final_draft_section",
                "exact_claim_text",
                "source_anchor",
                "evidence_type",
                "confidence",
                "notes",
            }
            if any(
                not isinstance(claim.get(field), str) or not claim.get(field)
                for field in ledger_fields
            ):
                errors.append(f"{path}: evidence ledger fields must be non-empty strings")
            if claim.get("evidence_type") not in {
                "paper-reported",
                "official-artifact",
                "user-provided",
                "direct-inference",
            }:
                errors.append(f"{path}: invalid evidence type")
            exact_claim = claim.get("exact_claim_text")
            if not isinstance(exact_claim, str) or exact_claim not in content:
                errors.append(f"{path}: claim text not found in draft: {claim.get('claim_id')}")
            claim_id = claim.get("claim_id")
            if isinstance(claim_id, str):
                ledger_ids.append(claim_id)
            section = claim.get("final_draft_section")
            if not isinstance(section, str) or f"## {section}" not in body:
                errors.append(f"{path}: claim section is absent: {claim_id}")
        if len(ledger_ids) != len(set(ledger_ids)):
            errors.append(f"{path}: evidence claim IDs must be unique")
        if _claim_ids(metadata.get("claim_ids")) != set(ledger_ids):
            errors.append(f"{path}: draft claim_ids must exactly match evidence ledger")
        ledger_by_id = {str(row.get("claim_id")): row for row in ledger if isinstance(row, dict)}
        for marker_id, paragraph in re.findall(
            r"<!-- claim:([A-Za-z0-9_-]+) -->\s*\n([^\n]+)", body
        ):
            traced = ledger_by_id.get(marker_id)
            if traced is None:
                errors.append(f"{path}: qualitative claim marker is not in evidence ledger")
                continue
            exact_text = traced.get("exact_claim_text")
            if not isinstance(exact_text, str) or exact_text not in paragraph:
                errors.append(f"{path}: qualitative claim marker does not trace its sentence")
            if traced.get("final_draft_section") not in {"해석", "한계와 외적 타당성"}:
                errors.append(f"{path}: qualitative claim marker uses the wrong section")
            if traced.get("evidence_type") != "direct-inference":
                errors.append(f"{path}: qualitative inference must use direct-inference evidence")
        method_fields = {"component", "role", "input", "output", "assumption", "source_anchor"}
        for row in methods:
            if not isinstance(row, dict):
                errors.append(f"{path}: method row must be an object")
            else:
                _required(row, method_fields, str(path), errors)
                if any(
                    not isinstance(row.get(field), str) or not row.get(field)
                    for field in method_fields
                ):
                    errors.append(f"{path}: method row fields must be non-empty strings")
        result_fields = {
            "claim_id",
            "result_claim",
            "setup",
            "exact_value",
            "comparator",
            "source_anchor",
            "caveat",
        }
        for row in results:
            if not isinstance(row, dict):
                errors.append(f"{path}: result row must be an object")
                continue
            _required(row, result_fields, str(path), errors)
            if any(
                not isinstance(row.get(field), str) or not row.get(field) for field in result_fields
            ):
                errors.append(f"{path}: result row fields must be non-empty strings")
            if row.get("claim_id") not in set(ledger_ids):
                errors.append(f"{path}: result claim_id is not in evidence ledger")
            result_claim = row.get("result_claim")
            if not isinstance(result_claim, str) or result_claim not in content:
                errors.append(f"{path}: result claim text is not in draft")
        for critique in critiques:
            if not isinstance(critique, dict):
                errors.append(f"{path}: critique row must be an object")
                continue
            critique_fields = {"critique", "label", "action", "reason", "final_prose_location"}
            _required(critique, critique_fields, str(path), errors)
            if any(
                not isinstance(critique.get(field), str) or not critique.get(field)
                for field in critique_fields
            ):
                errors.append(f"{path}: critique row fields must be non-empty strings")
            if critique.get("label") not in {
                "paper-evidenced",
                "direct inference from setup",
                "speculative",
            }:
                errors.append(f"{path}: invalid critique label")
            if critique.get("label") == "speculative" and critique.get("action") == "accepted":
                errors.append(f"{path}: speculative critique cannot enter final prose")
        numeric_body = body.split("## References", 1)[0]
        numeric_body = "\n".join(
            line
            for line in numeric_body.splitlines()
            if not line.startswith(("|", "#", "**Paper:", "<!--")) and "](" not in line
        )
        traced_sentences = {
            re.sub(r"\s+", " ", str(row.get(field, ""))).strip()
            for rows, field in ((ledger, "exact_claim_text"), (results, "result_claim"))
            for row in rows
            if isinstance(row, dict)
        }
        numeric_sentences: set[str] = set()
        for sentence in re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", numeric_body)):
            normalized = sentence.strip()
            normalized = re.sub(r"^\*\*TL;DR\*\*\s*—\s*", "", normalized)
            numeric_probe = re.sub(
                r"\b(?:Section|Sec\.?|Figure|Fig\.?|Table)\s*\d+(?:\.\d+)?",
                "",
                normalized,
            )
            numeric_probe = re.sub(
                r"\b(?:Veo\s*3|Veo\s*2|GPT-5(?:-Mini)?|o4-mini|3D|ImageNet-512|Kinetics-600)",
                "",
                numeric_probe,
            )
            if NUMBER_RE.search(numeric_probe):
                numeric_sentences.add(normalized)
        unsupported_sentences = sorted(numeric_sentences - traced_sentences)
        if unsupported_sentences:
            errors.append(f"{path}: unsupported numeric sentences {unsupported_sentences}")


def _validate_manifest(
    root: Path,
    editorial: dict[str, dict[str, Any]],
    errors: list[str],
    require_final: bool,
) -> None:
    data = _load_json(root / "approval-manifest.json", errors)
    if not isinstance(data, dict):
        return
    if data.get("publication_gate") != "blocked_paperwiki_unavailable":
        errors.append("publication gate must remain blocked_paperwiki_unavailable")
    items = data.get("items")
    if not isinstance(items, list) or len(items) != 12:
        errors.append("approval manifest must contain 12 items")
        return
    typed_items = [item for item in items if isinstance(item, dict)]
    if len(typed_items) != len(items):
        errors.append("approval manifest item must be an object")
    if {str(item.get("entry_id")) for item in typed_items} != set(editorial):
        errors.append("approval manifest must map one-to-one to editorial entries")
    for item in typed_items:
        entry_id = item.get("entry_id")
        entry = editorial.get(str(entry_id))
        if entry is not None:
            parity = {
                "local_path": "local_path",
                "proposed_slug": "proposed_slug",
                "company": "company",
                "entry_kind": "entry_kind",
                "paper_id": "paper_id",
                "proposed_order": "order",
            }
            for manifest_key, editorial_key in parity.items():
                if item.get(manifest_key) != entry.get(editorial_key):
                    errors.append(f"{entry_id}: manifest/editorial parity mismatch {manifest_key}")
        if item.get("user_approved") is not False or item.get("published") is not False:
            errors.append(f"{entry_id}: approval and published must be false")
        paperwiki = item.get("paperwiki", {})
        blog = item.get("blog", {})
        if paperwiki != {"status": "blocked_unavailable", "url": None}:
            errors.append(f"{entry_id}: PaperWiki state is unsafe")
        if blog != {"status": "not_attempted", "id": None, "url": None}:
            errors.append(f"{entry_id}: blog state is unsafe")
        preflight = item.get("local_preflight")
        if preflight != {"status": "ready", "warnings": []}:
            errors.append(f"{entry_id}: local preflight state is invalid")
        if item.get("evidence_status") != "ready":
            errors.append(f"{entry_id}: evidence status is not ready")
        review_status = item.get("independent_review_status")
        revision_status = item.get("revision_status")
        if require_final:
            if review_status != "approved" or revision_status != "applied_and_reverified":
                errors.append(f"{entry_id}: independent final review is not complete")
        elif review_status not in {"pending", "approved"}:
            errors.append(f"{entry_id}: independent review status is invalid")


def _validate_reports(root: Path, errors: list[str], require_final: bool) -> None:
    code_review = _load_json(root / "reports" / "code-review.json", errors)
    architecture = _load_json(root / "reports" / "architecture-invariant-audit.json", errors)
    critical_path = root / "reports" / "critical-review.md"
    try:
        critical = critical_path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"invalid critical review report: {exc}")
        critical = ""
    critical_match = re.search(
        r"<!-- structured-review:start -->\s*(\{.*?\})\s*<!-- structured-review:end -->",
        critical,
        re.DOTALL,
    )
    critical_data: Any = None
    if critical_match is not None:
        try:
            critical_data = json.loads(critical_match.group(1))
        except json.JSONDecodeError as exc:
            errors.append(f"critical review structured JSON is invalid: {exc}")
    if not isinstance(critical_data, dict):
        errors.append("critical review structured payload must be an object")
    if not isinstance(code_review, dict):
        errors.append("code review report must be an object")
    elif require_final and (
        code_review.get("status") != "complete" or code_review.get("recommendation") != "APPROVE"
    ):
        errors.append("final code-review gate is not APPROVE")
    elif not require_final and code_review.get("recommendation") not in {
        "PENDING",
        "APPROVE",
        "REQUEST_CHANGES",
        "BLOCK",
    }:
        errors.append("code-review recommendation is invalid")
    if isinstance(code_review, dict):
        review = code_review.get("independentReview")
        if not isinstance(review, dict):
            errors.append("code-review independent evidence must be an object")
        elif require_final and (
            review.get("agentRole") != "code-reviewer"
            or review.get("status") != "complete"
            or not isinstance(review.get("evidence"), str)
            or not review.get("evidence")
            or review.get("lane") == "implementation-revision-owner"
        ):
            errors.append("final code-review independent evidence is invalid")
    if not isinstance(architecture, dict):
        errors.append("architecture audit report must be an object")
    elif require_final and architecture.get("status") != "CLEAR":
        errors.append("final architecture gate is not CLEAR")
    elif not require_final and architecture.get("status") not in {"PENDING", "CLEAR", "BLOCK"}:
        errors.append("architecture audit status is invalid")
    if isinstance(architecture, dict):
        review = architecture.get("independentReview")
        invariants = architecture.get("invariants")
        if not isinstance(review, dict) or not isinstance(invariants, list):
            errors.append("architecture independent evidence and invariants must be structured")
        elif require_final:
            if (
                review.get("agentRole") != "architect"
                or review.get("status") != "complete"
                or not isinstance(review.get("evidence"), str)
                or not review.get("evidence")
                or review.get("lane") == "implementation-revision-owner"
            ):
                errors.append("final architecture independent evidence is invalid")
            invariant_fields = {
                "invariant",
                "status",
                "implementationEvidence",
                "testEvidence",
                "reviewEvidence",
            }
            for invariant in invariants:
                if (
                    not isinstance(invariant, dict)
                    or any(
                        not isinstance(invariant.get(field), str) or not invariant.get(field)
                        for field in invariant_fields
                    )
                    or invariant.get("status") != "proved"
                ):
                    errors.append("final architecture invariant proof is incomplete")
                    break
    if isinstance(critical_data, dict):
        lanes = critical_data.get("lanes")
        findings = critical_data.get("findings")
        if not isinstance(lanes, list) or not isinstance(findings, list):
            errors.append("critical review lanes and findings must be lists")
        else:
            finding_fields = {
                "findingId",
                "severity",
                "reason",
                "status",
                "disposition",
                "target",
                "revisionEvidence",
                "revalidationEvidence",
            }
            allowed_dispositions = {"accepted", "softened", "rejected"}
            for finding in findings:
                if not isinstance(finding, dict) or any(
                    not isinstance(finding.get(field), str) or not finding.get(field)
                    for field in finding_fields
                ):
                    errors.append("critical review finding evidence is incomplete")
                    break
                disposition = finding.get("disposition")
                if disposition not in allowed_dispositions:
                    errors.append("critical review finding disposition is invalid")
                    break
                if (
                    disposition in {"accepted", "softened"}
                    and finding.get("status") != "applied_and_reverified"
                ):
                    errors.append("accepted critical finding is not applied and reverified")
                    break
                if disposition in {"accepted", "softened"} and any(
                    "pending" in str(finding.get(field, "")).casefold()
                    for field in ("revisionEvidence", "revalidationEvidence")
                ):
                    errors.append("accepted critical finding has pending evidence")
                    break
                if disposition == "rejected" and not finding.get("reason"):
                    errors.append("rejected critical finding needs a reason")
                    break
        if isinstance(lanes, list) and isinstance(findings, list) and require_final:
            expected_roles = {"critic", "verifier", "revision-owner"}
            roles = {lane.get("agentRole") for lane in lanes if isinstance(lane, dict)}
            lane_names = [lane.get("lane") for lane in lanes if isinstance(lane, dict)]
            if roles != expected_roles or len(lane_names) != len(set(lane_names)):
                errors.append("critical review roles must be distinct and complete")
            for lane in lanes:
                if not isinstance(lane, dict) or (
                    lane.get("status") != "complete"
                    or not isinstance(lane.get("evidence"), str)
                    or not lane.get("evidence")
                ):
                    errors.append("critical review lane evidence is incomplete")
                    break
            if critical_data.get("finalStatus") != "complete":
                errors.append("final critical-review gate is incomplete")
    if require_final and isinstance(code_review, dict) and isinstance(architecture, dict):
        code_independent = code_review.get("independentReview")
        architecture_independent = architecture.get("independentReview")
        critical_lanes = critical_data.get("lanes", []) if isinstance(critical_data, dict) else []
        lane_records = [code_independent, architecture_independent, *critical_lanes]
        lane_ids = [record.get("lane") for record in lane_records if isinstance(record, dict)]
        normalized_lanes = [lane.casefold() for lane in lane_ids if isinstance(lane, str) and lane]
        if (
            len(lane_ids) != 5
            or any(not isinstance(lane, str) or not lane for lane in lane_ids)
            or len(set(normalized_lanes)) != 5
        ):
            errors.append("all independent review lane IDs must be globally distinct")
        required_prefix = {
            "code-reviewer": "independent-",
            "architect": "independent-",
            "critic": "independent-",
            "verifier": "independent-",
            "revision-owner": "implementation-",
        }
        for record in lane_records:
            if not isinstance(record, dict):
                continue
            role = record.get("agentRole")
            normalized_lane = str(record.get("lane", "")).casefold()
            if role not in required_prefix or not normalized_lane.startswith(
                required_prefix[str(role)]
            ):
                errors.append("review lane prefix does not match its role")
                break
            if role != "revision-owner" and (
                "implementation-owner" in normalized_lane or "self-review" in normalized_lane
            ):
                errors.append("independent reviewer cannot use a self-review lane")
                break


def validate(root: Path, *, require_final: bool = False) -> dict[str, Any]:
    """Return a deterministic validation report without mutating remote systems."""
    errors: list[str] = []
    try:
        drafts, evidence = _validate_structure(root, errors)
    except OSError as exc:
        return {"ready": False, "errors": [f"missing artifact structure: {exc}"]}
    candidates = _validate_inventory(root, errors)
    editorial = _validate_editorial(root, errors)
    preflight_ready = _validate_drafts(root, drafts, editorial, errors)
    _validate_evidence(root, evidence, candidates, errors)
    _validate_manifest(root, editorial, errors, False)
    _validate_reports(root, errors, False)
    structural_ready = not errors
    final_errors: list[str] = []
    if require_final:
        _validate_manifest(root, editorial, final_errors, True)
        _validate_reports(root, final_errors, True)
    final_ready = structural_ready and require_final and not final_errors
    all_errors = errors + final_errors
    return {
        "ready": final_ready if require_final else structural_ready,
        "validation_mode": "final" if require_final else "pre-review",
        "structural_ready": structural_ready,
        "final_ready": final_ready,
        "series_id": "1kpapers-company-series-2026-pilot",
        "counts": {"companies": 3, "drafts": len(drafts), "evidence_bundles": len(evidence)},
        "citability": {"ready": preflight_ready, "total": len(drafts), "warning_overrides": 0},
        "remote_mutations": 0,
        "publication": {"paperwiki": "blocked_unavailable", "blog": "not_attempted"},
        "errors": sorted(all_errors),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--mode", choices=("pre-review", "final"), default="pre-review")
    args = parser.parse_args()
    report = validate(args.root.resolve(), require_final=args.mode == "final")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
