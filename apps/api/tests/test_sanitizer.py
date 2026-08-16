"""Unit tests for sanitization utilities."""

import pytest
import json
from utils.sanitizer import (
    sanitize_string,
    sanitize_html,
    sanitize_url,
    sanitize_filename,
    sanitize_email,
    sanitize_dict,
    sanitize_list,
    sanitize_json_string,
)

pytestmark = pytest.mark.unit


class TestSanitizeString:
    """Tests for string sanitization."""
    
    @pytest.mark.unit
    def test_clean_string(self):
        assert sanitize_string("Hello World") == "Hello World"
    
    @pytest.mark.unit
    def test_remove_control_chars(self):
        result = sanitize_string("Hello\x00World")
        assert "\x00" not in result
        assert "HelloWorld" == result
    
    @pytest.mark.unit
    def test_preserve_newlines(self):
        result = sanitize_string("Hello\nWorld")
        assert "\n" in result
    
    @pytest.mark.unit
    def test_max_length(self):
        result = sanitize_string("Hello World", max_length=5)
        assert result == "Hello"
    
    @pytest.mark.unit
    def test_non_string_input(self):
        result = sanitize_string(123)
        assert result == "123"


class TestSanitizeHtml:
    """Tests for HTML sanitization."""
    
    @pytest.mark.unit
    def test_escape_html_tags(self):
        result = sanitize_html("<script>alert('xss')</script>")
        assert "<" not in result or "&lt;" in result
        assert ">" not in result or "&gt;" in result
    
    @pytest.mark.unit
    def test_escape_quotes(self):
        result = sanitize_html('Hello "World"')
        # Quotes should be escaped (either as &quot; or &#x27; or similar)
        assert "&quot;" in result or "&#" in result
    
    @pytest.mark.unit
    def test_clean_text(self):
        result = sanitize_html("Hello World")
        assert result == "Hello World"


class TestSanitizeUrl:
    """Tests for URL sanitization."""
    
    @pytest.mark.unit
    def test_valid_url(self):
        result = sanitize_url("https://example.com/path")
        assert result == "https://example.com/path"
    
    @pytest.mark.unit
    def test_remove_javascript_protocol(self):
        result = sanitize_url("javascript:alert('xss')")
        assert result == ""
    
    @pytest.mark.unit
    def test_remove_data_protocol(self):
        result = sanitize_url("data:text/html,<script>alert('xss')</script>")
        assert result == ""
    
    @pytest.mark.unit
    def test_remove_control_chars(self):
        result = sanitize_url("https://example.com\x00/path")
        assert "\x00" not in result
    
    @pytest.mark.unit
    def test_non_string_input(self):
        result = sanitize_url(123)
        assert result == ""


class TestSanitizeFilename:
    """Tests for filename sanitization."""
    
    @pytest.mark.unit
    def test_valid_filename(self):
        result = sanitize_filename("document.pdf")
        assert result == "document.pdf"
    
    @pytest.mark.unit
    def test_remove_path_traversal(self):
        result = sanitize_filename("../../etc/passwd")
        assert ".." not in result
    
    @pytest.mark.unit
    def test_remove_directory_separators(self):
        result = sanitize_filename("path/to/file.txt")
        assert "/" not in result
        assert "\\" not in result
    
    @pytest.mark.unit
    def test_remove_special_chars(self):
        result = sanitize_filename("file@#$%^&*.txt")
        assert "@" not in result
        assert "#" not in result
    
    @pytest.mark.unit
    def test_empty_filename(self):
        result = sanitize_filename("")
        assert result == "file"
    
    @pytest.mark.unit
    def test_max_length(self):
        result = sanitize_filename("a" * 300 + ".txt")
        assert len(result) <= 255


class TestSanitizeEmail:
    """Tests for email sanitization."""
    
    @pytest.mark.unit
    def test_lowercase_email(self):
        result = sanitize_email("User@Example.COM")
        assert result == "user@example.com"
    
    @pytest.mark.unit
    def test_remove_whitespace(self):
        result = sanitize_email("  user@example.com  ")
        assert result == "user@example.com"
    
    @pytest.mark.unit
    def test_non_string_input(self):
        result = sanitize_email(123)
        assert result == ""


class TestSanitizeDict:
    """Tests for dictionary sanitization."""
    
    @pytest.mark.unit
    def test_clean_dict(self):
        data = {"name": "John", "age": 30}
        result = sanitize_dict(data)
        assert result == data
    
    @pytest.mark.unit
    def test_sanitize_string_values(self):
        data = {"name": "John\x00", "tag": "<script>"}
        result = sanitize_dict(data)
        assert "\x00" not in result["name"]
    
    @pytest.mark.unit
    def test_nested_dict(self):
        data = {
            "user": {
                "name": "John",
                "contact": {
                    "email": "john@example.com"
                }
            }
        }
        result = sanitize_dict(data)
        assert result["user"]["contact"]["email"] == "john@example.com"
    
    @pytest.mark.unit
    def test_max_depth(self):
        # Create very deep nested dict
        data = {"a": {"b": {"c": {"d": {"e": "value"}}}}}
        result = sanitize_dict(data, max_depth=2)
        assert isinstance(result, dict)


class TestSanitizeList:
    """Tests for list sanitization."""
    
    @pytest.mark.unit
    def test_clean_list(self):
        data = ["a", "b", "c"]
        result = sanitize_list(data)
        assert result == data
    
    @pytest.mark.unit
    def test_sanitize_items(self):
        data = ["hello\x00", "<script>alert</script>"]
        result = sanitize_list(data)
        assert "\x00" not in result[0]
    
    @pytest.mark.unit
    def test_nested_list(self):
        data = [
            "item1",
            ["nested1", "nested2"],
            {"key": "value"}
        ]
        result = sanitize_list(data)
        assert len(result) == 3


class TestSanitizeJsonString:
    """Tests for JSON string sanitization."""
    
    @pytest.mark.unit
    def test_valid_json(self):
        json_str = '{"name": "John", "age": 30}'
        result = sanitize_json_string(json_str)
        parsed = json.loads(result)
        assert parsed["name"] == "John"
    
    @pytest.mark.unit
    def test_invalid_json(self):
        result = sanitize_json_string("{invalid json}")
        assert result == ""
    
    @pytest.mark.unit
    def test_sanitizes_content(self):
        json_str = '{"script": "<script>alert()</script>"}'
        result = sanitize_json_string(json_str)
        assert len(result) > 0
        parsed = json.loads(result)
        assert "script" in parsed
