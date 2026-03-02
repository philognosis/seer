"""
Tests for description optimizer
"""
from src.services.description.optimizer import DescriptionOptimizer


def test_remove_redundant_phrases():
    """Test removal of camera-referencing phrases"""
    optimizer = DescriptionOptimizer()
    text = "We see a man walking across the room."
    result = optimizer.optimize(text)
    assert "we see" not in result.lower()


def test_remove_filler_words():
    """Test removal of filler words"""
    optimizer = DescriptionOptimizer()
    text = "A very tall man really walks quite slowly."
    result = optimizer.optimize(text)
    assert "very" not in result.lower()
    assert "really" not in result.lower()
    assert "quite" not in result.lower()


def test_validate_good_description():
    """Test validation of a good description"""
    optimizer = DescriptionOptimizer()
    result = optimizer.validate_description("Sarah reaches for the doorknob.")
    assert result["is_valid"] is True
    assert len(result["issues"]) == 0


def test_validate_bad_description():
    """Test validation catches issues"""
    optimizer = DescriptionOptimizer()
    result = optimizer.validate_description("The camera pans to show a close-up.")
    assert result["is_valid"] is False
    assert any("camera" in issue.lower() for issue in result["issues"])


def test_validate_too_short():
    """Test validation of too-short description"""
    optimizer = DescriptionOptimizer()
    result = optimizer.validate_description("He walks.")
    # 2 words should be too short
    assert any("short" in issue.lower() for issue in result["issues"])


def test_trim_to_words():
    """Test word limit trimming"""
    optimizer = DescriptionOptimizer()
    text = "A long description that needs to be trimmed down to fit."
    result = optimizer.optimize(text, max_words=5)
    assert len(result.split()) <= 5
