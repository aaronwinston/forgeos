"""Unit tests for helper utilities."""

import pytest
from datetime import datetime, timedelta, timezone
from utils.helpers import (
    generate_id,
    generate_org_id,
    generate_project_id,
    generate_user_id,
    truncate_string,
    chunk_list,
    paginate_list,
    merge_dicts,
    flatten_dict,
    format_datetime,
    parse_datetime,
    get_time_delta_seconds,
    is_expired,
    safe_get,
)

pytestmark = pytest.mark.unit


class TestIdGeneration:
    """Tests for ID generation utilities."""
    
    @pytest.mark.unit
    def test_generate_id(self):
        id1 = generate_id()
        id2 = generate_id()
        assert id1 != id2
        assert len(id1) > 0
    
    @pytest.mark.unit
    def test_generate_id_with_prefix(self):
        id_with_prefix = generate_id("test")
        assert id_with_prefix.startswith("test_")
    
    @pytest.mark.unit
    def test_generate_org_id(self):
        org_id = generate_org_id()
        assert org_id.startswith("org_")
    
    @pytest.mark.unit
    def test_generate_project_id(self):
        proj_id = generate_project_id()
        assert proj_id.startswith("proj_")
    
    @pytest.mark.unit
    def test_generate_user_id(self):
        user_id = generate_user_id()
        assert user_id.startswith("user_")


class TestTruncateString:
    """Tests for string truncation."""
    
    @pytest.mark.unit
    def test_truncate_long_string(self):
        result = truncate_string("Hello World", 5)
        assert len(result) <= 5
        assert result.endswith("...")
    
    @pytest.mark.unit
    def test_no_truncate_short_string(self):
        result = truncate_string("Hi", 10)
        assert result == "Hi"
    
    @pytest.mark.unit
    def test_custom_suffix(self):
        result = truncate_string("Hello World", 8, ">>")
        assert result.endswith(">>")


class TestChunkList:
    """Tests for list chunking."""
    
    @pytest.mark.unit
    def test_chunk_evenly_divisible(self):
        items = list(range(10))
        chunks = chunk_list(items, 5)
        assert len(chunks) == 2
        assert chunks[0] == [0, 1, 2, 3, 4]
        assert chunks[1] == [5, 6, 7, 8, 9]
    
    @pytest.mark.unit
    def test_chunk_not_evenly_divisible(self):
        items = list(range(10))
        chunks = chunk_list(items, 3)
        assert len(chunks) == 4
        assert chunks[-1] == [9]
    
    @pytest.mark.unit
    def test_chunk_empty_list(self):
        chunks = chunk_list([], 5)
        assert chunks == []


class TestPaginateList:
    """Tests for list pagination."""
    
    @pytest.mark.unit
    def test_first_page(self):
        items = list(range(100))
        paginated, total = paginate_list(items, skip=0, limit=10)
        assert len(paginated) == 10
        assert total == 100
        assert paginated[0] == 0
    
    @pytest.mark.unit
    def test_middle_page(self):
        items = list(range(100))
        paginated, total = paginate_list(items, skip=20, limit=10)
        assert len(paginated) == 10
        assert paginated[0] == 20
    
    @pytest.mark.unit
    def test_last_page(self):
        items = list(range(100))
        paginated, total = paginate_list(items, skip=95, limit=10)
        assert len(paginated) == 5
        assert paginated[0] == 95


class TestMergeDicts:
    """Tests for dictionary merging."""
    
    @pytest.mark.unit
    def test_merge_two_dicts(self):
        d1 = {"a": 1, "b": 2}
        d2 = {"c": 3}
        result = merge_dicts(d1, d2)
        assert result == {"a": 1, "b": 2, "c": 3}
    
    @pytest.mark.unit
    def test_merge_override(self):
        d1 = {"a": 1}
        d2 = {"a": 2}
        result = merge_dicts(d1, d2)
        assert result["a"] == 2
    
    @pytest.mark.unit
    def test_merge_multiple(self):
        result = merge_dicts({"a": 1}, {"b": 2}, {"c": 3})
        assert result == {"a": 1, "b": 2, "c": 3}
    
    @pytest.mark.unit
    def test_merge_empty(self):
        result = merge_dicts({})
        assert result == {}


class TestFlattenDict:
    """Tests for dictionary flattening."""
    
    @pytest.mark.unit
    def test_flatten_nested_dict(self):
        data = {"user": {"name": "John", "email": "john@example.com"}}
        result = flatten_dict(data)
        assert result["user_name"] == "John"
        assert result["user_email"] == "john@example.com"
    
    @pytest.mark.unit
    def test_flatten_deeply_nested(self):
        data = {"level1": {"level2": {"level3": "value"}}}
        result = flatten_dict(data)
        assert result["level1_level2_level3"] == "value"
    
    @pytest.mark.unit
    def test_flatten_custom_separator(self):
        data = {"user": {"name": "John"}}
        result = flatten_dict(data, sep="-")
        assert "user-name" in result


class TestDatetimeFormatting:
    """Tests for datetime formatting."""
    
    @pytest.mark.unit
    def test_format_datetime(self):
        dt = datetime(2024, 1, 15, 14, 30, 45)
        result = format_datetime(dt)
        assert "2024-01-15" in result
        assert "14:30:45" in result
    
    @pytest.mark.unit
    def test_parse_datetime(self):
        result = parse_datetime("2024-01-15 14:30:45")
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
    
    @pytest.mark.unit
    def test_parse_invalid_datetime(self):
        result = parse_datetime("invalid")
        assert result is None


class TestTimeDelta:
    """Tests for time delta utilities."""
    
    @pytest.mark.unit
    def test_time_delta_minutes(self):
        seconds = get_time_delta_seconds(minutes=5)
        assert seconds == 300
    
    @pytest.mark.unit
    def test_time_delta_hours(self):
        seconds = get_time_delta_seconds(hours=1)
        assert seconds == 3600
    
    @pytest.mark.unit
    def test_time_delta_days(self):
        seconds = get_time_delta_seconds(days=1)
        assert seconds == 86400
    
    @pytest.mark.unit
    def test_time_delta_combined(self):
        seconds = get_time_delta_seconds(hours=1, minutes=30)
        assert seconds == 5400


class TestIsExpired:
    """Tests for expiration checking."""
    
    @pytest.mark.unit
    def test_not_expired(self):
        created_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        assert is_expired(created_at, 3600) is False
    
    @pytest.mark.unit
    def test_expired(self):
        created_at = datetime.now(timezone.utc) - timedelta(hours=2)
        assert is_expired(created_at, 3600) is True
    
    @pytest.mark.unit
    def test_invalid_input(self):
        assert is_expired("invalid", 3600) is True


class TestSafeGet:
    """Tests for safe dictionary get."""
    
    @pytest.mark.unit
    def test_get_existing_key(self):
        data = {"name": "John", "age": 30}
        result = safe_get(data, "name")
        assert result == "John"
    
    @pytest.mark.unit
    def test_get_missing_key(self):
        data = {"name": "John"}
        result = safe_get(data, "age", default=0)
        assert result == 0
    
    @pytest.mark.unit
    def test_get_with_type_conversion(self):
        data = {"age": "30"}
        result = safe_get(data, "age", type_=int)
        assert result == 30
        assert isinstance(result, int)
    
    @pytest.mark.unit
    def test_get_non_dict(self):
        result = safe_get("not a dict", "key", default="default")
        assert result == "default"
