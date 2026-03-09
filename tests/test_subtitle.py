"""Tests for subtitle formatting functions."""

import pytest
from bili_cli.client import _format_time, _format_srt_time, format_subtitle_timeline


class TestFormatTime:
    """Tests for _format_time function (MM:SS.mmm format)."""

    def test_zero_seconds(self):
        assert _format_time(0.0) == "00:00.000"

    def test_simple_seconds(self):
        assert _format_time(2.5) == "00:02.500"
        assert _format_time(5.0) == "00:05.000"

    def test_one_minute(self):
        assert _format_time(60.0) == "01:00.000"
        assert _format_time(65.333) == "01:05.333"

    def test_multiple_minutes(self):
        assert _format_time(125.789) == "02:05.789"
        assert _format_time(300.0) == "05:00.000"

    def test_milliseconds_precision(self):
        assert _format_time(1.001) == "00:01.001"
        assert _format_time(1.999) == "00:01.999"


class TestFormatSrtTime:
    """Tests for _format_srt_time function (HH:MM:SS,mmm format)."""

    def test_zero_seconds(self):
        assert _format_srt_time(0.0) == "00:00:00,000"

    def test_simple_seconds(self):
        assert _format_srt_time(2.5) == "00:00:02,500"
        assert _format_srt_time(5.0) == "00:00:05,000"

    def test_minutes(self):
        assert _format_srt_time(60.0) == "00:01:00,000"
        assert _format_srt_time(65.333) == "00:01:05,333"

    def test_hours(self):
        assert _format_srt_time(3600.0) == "01:00:00,000"
        assert _format_srt_time(3665.789) == "01:01:05,789"

    def test_comma_decimal_separator(self):
        """SRT uses comma instead of dot for decimal separator."""
        result = _format_srt_time(1.5)
        assert "," in result
        assert "." not in result


class TestFormatSubtitleTimeline:
    """Tests for format_subtitle_timeline function."""

    def test_empty_list(self):
        assert format_subtitle_timeline([]) == ""

    def test_none_list(self):
        assert format_subtitle_timeline(None) == ""

    def test_timeline_format_basic(self):
        raw = [
            {"content": "Hello", "from": 0.0, "to": 2.5},
        ]
        result = format_subtitle_timeline(raw, format="timeline")
        assert "[00:00.000 --> 00:02.500] Hello" in result

    def test_timeline_format_multiple(self):
        raw = [
            {"content": "First", "from": 0.0, "to": 2.0},
            {"content": "Second", "from": 2.0, "to": 5.5},
        ]
        result = format_subtitle_timeline(raw, format="timeline")
        lines = result.split("\n")
        assert "[00:00.000 --> 00:02.000] First" in lines[0]
        assert "[00:02.000 --> 00:05.500] Second" in lines[1]

    def test_srt_format_basic(self):
        raw = [
            {"content": "Hello", "from": 0.0, "to": 2.5},
        ]
        result = format_subtitle_timeline(raw, format="srt")
        assert "1" in result
        assert "00:00:00,000 --> 00:00:02,500" in result
        assert "Hello" in result

    def test_srt_format_multiple(self):
        raw = [
            {"content": "First", "from": 0.0, "to": 2.0},
            {"content": "Second", "from": 2.0, "to": 5.0},
        ]
        result = format_subtitle_timeline(raw, format="srt")
        lines = result.split("\n")
        # SRT format: index, time, content, empty line
        assert "1" in lines[0]
        assert "2" in lines[4]
        assert "First" in lines[2]
        assert "Second" in lines[6]

    def test_srt_format_empty_lines(self):
        """SRT format should have empty lines between entries."""
        raw = [
            {"content": "Test", "from": 0.0, "to": 1.0},
        ]
        result = format_subtitle_timeline(raw, format="srt")
        # Should end with empty line
        assert result.endswith("\n")

    def test_default_format_is_timeline(self):
        raw = [
            {"content": "Test", "from": 0.0, "to": 1.0},
        ]
        result = format_subtitle_timeline(raw)  # No format specified
        assert "[00:00.000 --> 00:01.000] Test" == result

    def test_chinese_content(self):
        raw = [
            {"content": "你好世界", "from": 0.0, "to": 2.0},
        ]
        result = format_subtitle_timeline(raw, format="timeline")
        assert "你好世界" in result

    def test_missing_fields(self):
        """Handle missing 'from' or 'to' fields gracefully."""
        raw = [
            {"content": "Test"},  # Missing from/to
        ]
        result = format_subtitle_timeline(raw, format="timeline")
        assert "[00:00.000 --> 00:00.000] Test" == result

    def test_long_duration(self):
        """Test with very long duration (hours)."""
        raw = [
            {"content": "Long video", "from": 3661.5, "to": 3665.789},
        ]
        result = format_subtitle_timeline(raw, format="timeline")
        assert "[61:01.500 --> 61:05.789] Long video" in result


class TestSubtitleDataStructure:
    """Tests to verify subtitle data structure handling."""

    def test_typical_subtitle_item(self):
        """Test with typical Bilibili subtitle item structure."""
        raw = [
            {
                "content": "欢迎观看本视频",
                "from": 0.0,
                "to": 2.5,
                "location": 2,
                "content_type": "text",
            },
            {
                "content": "今天我们来聊聊 Python",
                "from": 2.5,
                "to": 5.0,
                "location": 2,
                "content_type": "text",
            },
        ]
        result = format_subtitle_timeline(raw, format="timeline")
        assert "欢迎观看本视频" in result
        assert "今天我们来聊聊 Python" in result
        assert "[00:00.000 --> 00:02.500]" in result
        assert "[00:02.500 --> 00:05.000]" in result
