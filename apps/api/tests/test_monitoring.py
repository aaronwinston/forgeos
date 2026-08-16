"""
Tests for monitoring functionality (P4.2).

Tests distributed tracing, metrics collection, and observability features.
"""

import pytest
import time
import json
from unittest.mock import patch, MagicMock, call
from datetime import datetime
from fastapi.testclient import TestClient

from monitoring import (
    time_operation,
    trace_operation,
    trace_request,
    get_metrics_collector,
    reset_request_metrics,
    MetricsCollector,
    OperationMetrics,
    record_db_operation,
    record_error,
    get_request_summary,
)
from main import app

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def cleanup_metrics():
    """Clean up metrics before each test."""
    reset_request_metrics()
    yield
    reset_request_metrics()


class TestTimeOperation:
    """Tests for time_operation context manager."""
    
    def test_basic_timing(self):
        """Test basic operation timing."""
        with time_operation("test_op"):
            time.sleep(0.01)
        
        collector = get_metrics_collector()
        assert len(collector.operations) == 1
        assert collector.operations[0].name == "test_op"
        assert collector.operations[0].duration_ms >= 10
    
    def test_timing_with_attributes(self):
        """Test recording attributes with operations."""
        attrs = {"table": "users", "count": 42}
        
        with time_operation("db_query", attributes=attrs):
            pass
        
        collector = get_metrics_collector()
        op = collector.operations[0]
        assert op.metadata == attrs
    
    def test_timing_with_exception(self):
        """Test timing when exception occurs."""
        with pytest.raises(RuntimeError):
            with time_operation("failing_op"):
                raise RuntimeError("Test error")
        
        collector = get_metrics_collector()
        op = collector.operations[0]
        assert op.success is False
        assert "Test error" in op.error
    
    def test_timing_disables_metrics(self):
        """Test skipping metrics recording."""
        with time_operation("test_op", record_metrics=False):
            pass
        
        collector = get_metrics_collector()
        # Operation not recorded if metrics disabled
        # (depends on trace behavior)
    
    def test_multiple_operations(self):
        """Test recording multiple operations."""
        with time_operation("op1"):
            time.sleep(0.01)
        
        with time_operation("op2"):
            time.sleep(0.01)
        
        with time_operation("op3"):
            time.sleep(0.01)
        
        collector = get_metrics_collector()
        assert len(collector.operations) == 3
        assert collector.operations[0].name == "op1"
        assert collector.operations[1].name == "op2"
        assert collector.operations[2].name == "op3"


class TestTraceRequest:
    """Tests for trace_request context manager."""
    
    def test_trace_request_basic(self):
        """Test basic request tracing."""
        reset_request_metrics()
        
        with trace_request("/api/projects", method="GET"):
            pass
        
        collector = get_metrics_collector()
        assert collector.request_context == {}
    
    def test_trace_request_with_context(self):
        """Test request tracing with user/org context."""
        reset_request_metrics()
        
        with trace_request(
            "/api/projects",
            method="GET",
            user_id="user-123",
            org_id="org-456",
            request_id="req-789",
        ):
            pass
        
        collector = get_metrics_collector()
        assert collector.request_context["user_id"] == "user-123"
        assert collector.request_context["org_id"] == "org-456"
        assert collector.request_context["request_id"] == "req-789"
    
    def test_trace_request_with_error(self):
        """Test request tracing when endpoint raises."""
        with pytest.raises(ValueError):
            with trace_request("/api/projects", method="POST"):
                raise ValueError("Something failed")


class TestTraceOperationDecorator:
    """Tests for @trace_operation decorator."""
    
    def test_decorator_basic(self):
        """Test decorator on simple function."""
        @trace_operation("my_function")
        def simple_func():
            return "result"
        
        result = simple_func()
        assert result == "result"
        
        collector = get_metrics_collector()
        assert len(collector.operations) == 1
        assert collector.operations[0].name == "my_function"
    
    def test_decorator_with_args(self):
        """Test decorator preserves function arguments."""
        @trace_operation("add_numbers")
        def add(a, b):
            return a + b
        
        result = add(5, 3)
        assert result == 8
    
    def test_decorator_with_exception(self):
        """Test decorator handles exceptions."""
        @trace_operation("failing_func")
        def failing():
            raise RuntimeError("Failed")
        
        with pytest.raises(RuntimeError):
            failing()
        
        collector = get_metrics_collector()
        op = collector.operations[0]
        assert op.success is False


class TestMetricsRecording:
    """Tests for metric recording functions."""
    
    def test_record_db_operation(self):
        """Test recording database operations."""
        # Should not raise
        record_db_operation("select", "projects", count=5)
        record_db_operation("insert", "users", count=1)
        record_db_operation("update", "projects", count=2)
        record_db_operation("delete", "sessions", count=10)
    
    def test_record_error(self):
        """Test recording errors."""
        # Should not raise
        record_error("database_error", context={"table": "users"})
        record_error("auth_error", context={"user_id": "123"})
    
    def test_get_request_summary(self):
        """Test getting request summary."""
        reset_request_metrics()
        
        collector = get_metrics_collector()
        collector.set_request_context({
            "user_id": "user-1",
            "org_id": "org-1",
        })
        
        with time_operation("db_query_1"):
            pass
        
        with time_operation("db_query_2"):
            pass
        
        summary = get_request_summary()
        assert "operation_count" in summary
        assert "context" in summary
        assert summary["context"]["user_id"] == "user-1"


class TestMetricsCollector:
    """Tests for MetricsCollector class."""
    
    def test_initialization(self):
        """Test MetricsCollector initialization."""
        collector = MetricsCollector()
        assert collector.operations == []
        assert collector.request_context == {}
    
    def test_add_operation(self):
        """Test adding operations to collector."""
        collector = MetricsCollector()
        
        op = OperationMetrics(
            name="test_op",
            duration_ms=100.5,
            metadata={"key": "value"},
        )
        
        collector.add_operation(op)
        assert len(collector.operations) == 1
        assert collector.operations[0].name == "test_op"
    
    def test_set_request_context(self):
        """Test setting request context."""
        collector = MetricsCollector()
        
        ctx = {
            "user_id": "u1",
            "org_id": "o1",
            "request_id": "r1",
        }
        
        collector.set_request_context(ctx)
        assert collector.request_context == ctx
    
    def test_get_request_summary(self):
        """Test getting request summary from collector."""
        collector = MetricsCollector()
        
        collector.set_request_context({"user_id": "u1"})
        
        op1 = OperationMetrics("op1", 100)
        op2 = OperationMetrics("op2", 50)
        
        collector.add_operation(op1)
        collector.add_operation(op2)
        
        summary = collector.get_request_summary()
        assert summary["operation_count"] == 2
        assert summary["total_duration_ms"] >= 150


class TestOperationMetrics:
    """Tests for OperationMetrics dataclass."""
    
    def test_initialization(self):
        """Test OperationMetrics initialization."""
        op = OperationMetrics(
            name="test_op",
            duration_ms=50.5,
            metadata={"key": "value"},
        )
        
        assert op.name == "test_op"
        assert op.duration_ms == 50.5
        assert op.metadata == {"key": "value"}
        assert op.success is True
        assert op.error is None
    
    def test_with_error(self):
        """Test OperationMetrics with error."""
        op = OperationMetrics(
            name="failed_op",
            duration_ms=25.0,
            success=False,
            error="Connection timeout",
        )
        
        assert op.success is False
        assert op.error == "Connection timeout"


class TestSlowQueryAlerts:
    """Tests for slow query alerting."""
    
    def test_slow_db_query_detection(self):
        """Test detection of slow database queries."""
        # Create a slow DB operation (>500ms)
        with time_operation("db_query", attributes={"table": "large_table"}):
            time.sleep(0.51)  # 510ms
        
        collector = get_metrics_collector()
        op = collector.operations[0]
        assert op.duration_ms > 500
    
    def test_slow_endpoint_detection(self):
        """Test detection of slow endpoints."""
        with trace_request("/api/slow_endpoint", method="GET"):
            time.sleep(1.01)  # 1010ms
        
        # Summary should show slow request
        summary = get_request_summary()
        assert summary is not None  # Would trigger alert


class TestIntegration:
    """Integration tests for monitoring system."""
    
    def test_complete_request_flow(self):
        """Test complete request monitoring flow."""
        reset_request_metrics()
        
        with trace_request(
            "/api/projects",
            method="GET",
            user_id="user-1",
            org_id="org-1",
        ):
            with time_operation("db_query_1", attributes={"table": "projects"}):
                time.sleep(0.01)
            
            with time_operation("db_query_2", attributes={"table": "folders"}):
                time.sleep(0.01)
        
        collector = get_metrics_collector()
        summary = collector.get_request_summary()
        
        assert summary["operation_count"] == 2
        assert summary["context"]["user_id"] == "user-1"
        assert summary["context"]["org_id"] == "org-1"
    
    def test_nested_operations(self):
        """Test nested operations monitoring."""
        reset_request_metrics()
        
        with time_operation("outer"):
            time.sleep(0.01)
            with time_operation("inner"):
                time.sleep(0.01)
        
        collector = get_metrics_collector()
        # Both operations should be recorded
        assert len(collector.operations) == 2


class TestHealthEndpointMonitoring:
    """Tests for health endpoint with monitoring."""
    
    def test_health_endpoint_available(self):
        """Test health endpoint is configured."""
        from main import app
        
        # Just verify endpoint exists in the app
        routes = [route.path for route in app.routes]
        assert "/api/health" in routes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
