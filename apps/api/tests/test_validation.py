"""Unit tests for validation utilities."""

import pytest
from utils.validation import (
    validate_email,
    validate_password,
    validate_url,
    validate_org_slug,
    validate_project_name,
    validate_object_id,
    validate_pagination,
    validate_json_field,
)

pytestmark = pytest.mark.unit


class TestValidateEmail:
    """Tests for email validation."""
    
    @pytest.mark.unit
    def test_valid_email(self):
        assert validate_email("user@example.com") is True
        assert validate_email("test.user+tag@sub.example.co.uk") is True
    
    @pytest.mark.unit
    def test_invalid_email(self):
        assert validate_email("invalid") is False
        assert validate_email("@example.com") is False
        assert validate_email("user@") is False
        assert validate_email("user @example.com") is False


class TestValidatePassword:
    """Tests for password validation."""
    
    @pytest.mark.unit
    def test_valid_password(self):
        is_valid, msg = validate_password("MyPassword123")
        assert is_valid is True
        assert msg is None
    
    @pytest.mark.unit
    def test_password_too_short(self):
        is_valid, msg = validate_password("Short1")
        assert is_valid is False
        assert "at least" in msg.lower()
    
    @pytest.mark.unit
    def test_password_missing_uppercase(self):
        is_valid, msg = validate_password("mypassword123")
        assert is_valid is False
        assert "uppercase" in msg.lower()
    
    @pytest.mark.unit
    def test_password_missing_lowercase(self):
        is_valid, msg = validate_password("MYPASSWORD123")
        assert is_valid is False
        assert "lowercase" in msg.lower()
    
    @pytest.mark.unit
    def test_password_missing_digit(self):
        is_valid, msg = validate_password("MyPassword")
        assert is_valid is False
        assert "digit" in msg.lower()


class TestValidateUrl:
    """Tests for URL validation."""
    
    @pytest.mark.unit
    def test_valid_url(self):
        assert validate_url("http://example.com") is True
        assert validate_url("https://example.com/path?query=1") is True
        assert validate_url("https://sub.example.co.uk:8080/path") is True
    
    @pytest.mark.unit
    def test_invalid_url(self):
        assert validate_url("not a url") is False
        assert validate_url("ftp://example.com") is False
        assert validate_url("example.com") is False


class TestValidateOrgSlug:
    """Tests for organization slug validation."""
    
    @pytest.mark.unit
    def test_valid_slug(self):
        is_valid, msg = validate_org_slug("my-org")
        assert is_valid is True
        assert msg is None
    
    @pytest.mark.unit
    def test_slug_too_short(self):
        is_valid, msg = validate_org_slug("ab")
        assert is_valid is False
        assert "at least 3" in msg.lower()
    
    @pytest.mark.unit
    def test_slug_too_long(self):
        is_valid, msg = validate_org_slug("a" * 51)
        assert is_valid is False
        assert "exceed 50" in msg.lower()
    
    @pytest.mark.unit
    def test_slug_invalid_chars(self):
        is_valid, msg = validate_org_slug("my_org")
        assert is_valid is False
        assert "lowercase" in msg.lower() or "hyphen" in msg.lower()
    
    @pytest.mark.unit
    def test_slug_starts_with_hyphen(self):
        is_valid, msg = validate_org_slug("-myorg")
        assert is_valid is False
        assert "start" in msg.lower()
    
    @pytest.mark.unit
    def test_slug_ends_with_hyphen(self):
        is_valid, msg = validate_org_slug("myorg-")
        assert is_valid is False
        assert "end" in msg.lower()


class TestValidateProjectName:
    """Tests for project name validation."""
    
    @pytest.mark.unit
    def test_valid_name(self):
        is_valid, msg = validate_project_name("My Project")
        assert is_valid is True
        assert msg is None
    
    @pytest.mark.unit
    def test_empty_name(self):
        is_valid, msg = validate_project_name("")
        assert is_valid is False
        assert "empty" in msg.lower()
    
    @pytest.mark.unit
    def test_name_too_long(self):
        is_valid, msg = validate_project_name("a" * 256)
        assert is_valid is False
        assert "exceed 255" in msg.lower()


class TestValidateObjectId:
    """Tests for object ID validation."""
    
    @pytest.mark.unit
    def test_valid_id(self):
        assert validate_object_id("abc123") is True
        assert validate_object_id("project-12345") is True
    
    @pytest.mark.unit
    def test_invalid_id(self):
        assert validate_object_id("") is False
        assert validate_object_id(123) is False
        assert validate_object_id("a" * 256) is False


class TestValidatePagination:
    """Tests for pagination parameter validation."""
    
    @pytest.mark.unit
    def test_valid_pagination(self):
        is_valid, msg = validate_pagination(0, 20)
        assert is_valid is True
        assert msg is None
    
    @pytest.mark.unit
    def test_negative_skip(self):
        is_valid, msg = validate_pagination(-1, 20)
        assert is_valid is False
        assert "non-negative" in msg.lower()
    
    @pytest.mark.unit
    def test_invalid_limit(self):
        is_valid, msg = validate_pagination(0, 0)
        assert is_valid is False
        assert "at least 1" in msg.lower()
    
    @pytest.mark.unit
    def test_limit_too_high(self):
        is_valid, msg = validate_pagination(0, 1001)
        assert is_valid is False
        assert "exceed 1000" in msg.lower()


class TestValidateJsonField:
    """Tests for JSON field validation."""
    
    @pytest.mark.unit
    def test_valid_json_types(self):
        assert validate_json_field({"key": "value"}) is True
        assert validate_json_field([1, 2, 3]) is True
        assert validate_json_field("string") is True
        assert validate_json_field(123) is True
        assert validate_json_field(None) is True
    
    @pytest.mark.unit
    def test_nested_json(self):
        data = {
            "nested": {
                "items": [1, 2, {"key": "value"}]
            }
        }
        assert validate_json_field(data) is True
