"""
Tests for gap analyzer service
"""
from src.services.audio.gap_analyzer import DescriptionSlot, GapAnalyzer


def test_estimate_duration():
    """Test speech duration estimation"""
    analyzer = GapAnalyzer()
    # At 2.5 words per second, 5 words = 2 seconds
    assert analyzer.estimate_duration("one two three four five") == 2.0


def test_trim_to_fit():
    """Test text trimming to fit duration"""
    analyzer = GapAnalyzer()
    text = "The character walks across the room. She picks up a book."
    # At 2.5 wps, 2 seconds = 5 words max
    trimmed = analyzer.trim_to_fit(text, max_duration=2.0)
    words = trimmed.split()
    assert len(words) <= 5


def test_estimate_duration_with_speed():
    """Test duration estimation with speed multiplier"""
    analyzer = GapAnalyzer()
    # At 1.3x speed, same text should take less time
    normal = analyzer.estimate_duration("one two three four five")
    fast = analyzer.estimate_duration("one two three four five", speed_multiplier=1.3)
    assert fast < normal
