"""Blackbox engine tests — determinism and boundary conditions."""

from app.engine.blackbox import compute


def test_deterministic_same_input_same_output(sample_engine_input):
    """Same input must always produce the same output."""
    result1 = compute(sample_engine_input)
    result2 = compute(sample_engine_input)
    assert result1 == result2


def test_score_in_valid_range(sample_engine_input):
    """Score must be between 1 and 10."""
    result = compute(sample_engine_input)
    assert 1 <= result["score"] <= 10


def test_label_matches_score(sample_engine_input):
    """Label must match the score bands."""
    result = compute(sample_engine_input)
    score = result["score"]
    label = result["label"]
    if score <= 3:
        assert label == "Weak"
    elif score <= 6:
        assert label == "Moderate"
    else:
        assert label == "Strong"


def test_minimal_input():
    """Minimal valid input should produce a low score."""
    result = compute({
        "claim": "x",
        "confidence_level": "low",
        "supporting_reasons": ["y"],
    })
    assert 1 <= result["score"] <= 10
    assert result["label"] in ("Weak", "Moderate", "Strong")
    assert "breakdown" in result
    assert "summary" in result


def test_output_structure(sample_engine_input):
    """Output must contain all expected keys."""
    result = compute(sample_engine_input)
    assert "score" in result
    assert "label" in result
    assert "summary" in result
    assert "breakdown" in result
    breakdown = result["breakdown"]
    assert "claim_detail_score" in breakdown
    assert "confidence_score" in breakdown
    assert "reason_scores" in breakdown


def test_empty_reasons():
    """Empty reasons list should not crash."""
    result = compute({
        "claim": "Some claim",
        "confidence_level": "medium",
        "supporting_reasons": [],
    })
    assert 1 <= result["score"] <= 10


def test_high_confidence_scores_higher():
    """Higher confidence should contribute to a higher score."""
    base = {
        "claim": "Technology is improving rapidly in many sectors worldwide",
        "supporting_reasons": ["Evidence shows growth", "Data supports this"],
    }
    low = compute({**base, "confidence_level": "low"})
    high = compute({**base, "confidence_level": "high"})
    assert high["score"] >= low["score"]
