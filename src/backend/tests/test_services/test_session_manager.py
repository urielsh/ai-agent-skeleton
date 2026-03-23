"""Session manager tests."""

from app.services.session_manager import compute_missing_fields, merge_drafts


def test_compute_missing_fields_all_missing():
    assert compute_missing_fields({}) == [
        "claim", "confidence_level", "supporting_reasons"
    ]


def test_compute_missing_fields_partial():
    draft = {"claim": "test claim"}
    missing = compute_missing_fields(draft)
    assert "claim" not in missing
    assert "confidence_level" in missing
    assert "supporting_reasons" in missing


def test_compute_missing_fields_complete():
    draft = {
        "claim": "test",
        "confidence_level": "high",
        "supporting_reasons": ["reason 1"],
    }
    assert compute_missing_fields(draft) == []


def test_compute_missing_fields_empty_string():
    draft = {"claim": "", "confidence_level": "low", "supporting_reasons": ["r"]}
    missing = compute_missing_fields(draft)
    assert "claim" in missing


def test_compute_missing_fields_empty_list():
    draft = {"claim": "test", "confidence_level": "low", "supporting_reasons": []}
    missing = compute_missing_fields(draft)
    assert "supporting_reasons" in missing


def test_merge_drafts_basic():
    base = {"claim": "old"}
    updates = {"claim": "new", "domain": "tech"}
    result = merge_drafts(base, updates)
    assert result["claim"] == "new"
    assert result["domain"] == "tech"


def test_merge_drafts_skips_none():
    base = {"claim": "keep"}
    updates = {"claim": None, "domain": "tech"}
    result = merge_drafts(base, updates)
    assert result["claim"] == "keep"
    assert result["domain"] == "tech"
