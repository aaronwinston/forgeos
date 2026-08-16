"""
ForgeOS — Performance monitoring, tracing, and metrics collection (P4.2).

Provides context managers for timing operations, distributed tracing,
and metrics collection/reporting for request latency, database queries,
and background jobs.
"""

import time
import logging
from contextlib import contextmanager
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import wraps
import json

from opentelemetry import trace, metrics
from opentelemetry.trace import Status, StatusCode

logger = logging.getLogger(__name__)
tracer = trace.get_tracer("forgeos.monitoring")
meter = metrics.get_meter("forgeos.monitoring")


# Create metrics that will be exported
request_counter = meter.create_counter(
    "http_requests_total",
    description="Total HTTP requests",
    unit="1"
)

request_duration_histogram = meter.create_histogram(
    "http_request_duration_ms",
    description="HTTP request duration",
    unit="ms"
)

db_query_counter = meter.create_counter(
    "db_queries_total",
    description="Total database queries",
    unit="1"
)

db_query_duration_histogram = meter.create_histogram(
    "db_query_duration_ms",
    description="Database query duration",
    unit="ms"
)

db_connection_pool_gauge = meter.create_gauge(
    "db_connection_pool_size",
    description="Database connection pool size",
    unit="1"
)

celery_task_counter = meter.create_counter(
    "celery_tasks_total",
    description="Total Celery tasks executed",
    unit="1"
)

celery_task_duration_histogram = meter.create_histogram(
    "celery_task_duration_ms",
    description="Celery task duration",
    unit="ms"
)

errors_counter = meter.create_counter(
    "errors_total",
    description="Total errors",
    unit="1"
)


@dataclass
class OperationMetrics:
    """Metrics for a timed operation."""
    name: str
    duration_ms: float
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None


class MetricsCollector:
    """Collects and reports performance metrics."""
    
    def __init__(self):
        self.operations: list[OperationMetrics] = []
        self.request_context: Dict[str, Any] = {}
    
    def add_operation(self, operation: OperationMetrics):
        """Record an operation metric."""
        self.operations.append(operation)
        logger.debug(
            f"Operation: {operation.name} - {operation.duration_ms:.2f}ms - "
            f"Success: {operation.success}"
        )
    
    def set_request_context(self, context: Dict[str, Any]):
        """Set request-level context (user_id, org_id, request_id)."""
        self.request_context = context
    
    def get_request_summary(self) -> Dict[str, Any]:
        """Get summary of all operations in current request."""
        if not self.operations:
            return {}
        
        total_duration = sum(op.duration_ms for op in self.operations)
        db_queries = [op for op in self.operations if op.name.startswith("db_")]
        
        return {
            "total_duration_ms": total_duration,
            "operation_count": len(self.operations),
            "db_query_count": len(db_queries),
            "db_total_duration_ms": sum(op.duration_ms for op in db_queries),
            "context": self.request_context,
        }


_metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    return _metrics_collector


@contextmanager
def time_operation(
    operation_name: str,
    attributes: Optional[Dict[str, Any]] = None,
    record_metrics: bool = True,
    record_trace: bool = True,
):
    """
    Context manager for timing an operation and creating a trace span.
    
    Usage:
        with time_operation("db_query", attributes={"table": "projects"}):
            projects = session.exec(select(Project)).all()
    """
    span = None
    attributes = attributes or {}
    start_time = time.time()
    
    try:
        if record_trace:
            span = tracer.start_span(operation_name)
            for key, value in attributes.items():
                span.set_attribute(key, value)
        
        yield
        
        duration_ms = (time.time() - start_time) * 1000
        
        if record_metrics:
            operation = OperationMetrics(
                name=operation_name,
                duration_ms=duration_ms,
                metadata=attributes,
                success=True,
            )
            _metrics_collector.add_operation(operation)
            
            # Update OpenTelemetry metrics
            if "db_" in operation_name:
                db_query_counter.add(1, {"operation": operation_name})
                db_query_duration_histogram.record(duration_ms, {"operation": operation_name})
                
                # Alert if query is slow (>500ms)
                if duration_ms > 500:
                    logger.warning(
                        f"Slow database query: {operation_name} took {duration_ms:.2f}ms",
                        extra={"attributes": attributes}
                    )
            elif "celery_" in operation_name:
                celery_task_counter.add(1, {"task": operation_name})
                celery_task_duration_histogram.record(duration_ms, {"task": operation_name})
                
                # Alert if task is slow (>10s)
                if duration_ms > 10000:
                    logger.warning(
                        f"Slow Celery task: {operation_name} took {duration_ms:.2f}ms",
                        extra={"attributes": attributes}
                    )
        
        if span:
            span.end()
    
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        
        if record_metrics:
            operation = OperationMetrics(
                name=operation_name,
                duration_ms=duration_ms,
                metadata=attributes,
                success=False,
                error=str(e),
            )
            _metrics_collector.add_operation(operation)
            errors_counter.add(1, {"operation": operation_name, "error_type": type(e).__name__})
        
        if span:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.end()
        
        raise


@contextmanager
def trace_request(
    endpoint: str,
    method: str = "GET",
    user_id: Optional[str] = None,
    org_id: Optional[str] = None,
    request_id: Optional[str] = None,
):
    """
    Context manager for tracing an entire request.
    
    Sets up distributed tracing with user, org, and request context.
    
    Usage:
        with trace_request("/api/projects", method="GET", user_id=user_id, org_id=org_id):
            # endpoint logic
    """
    # Set request context for metrics
    context = {}
    if user_id:
        context["user_id"] = user_id
    if org_id:
        context["org_id"] = org_id
    if request_id:
        context["request_id"] = request_id
    
    _metrics_collector.set_request_context(context)
    
    with tracer.start_as_current_span(f"{method} {endpoint}") as span:
        span.set_attribute("http.method", method)
        span.set_attribute("http.url", endpoint)
        
        if user_id:
            span.set_attribute("user_id", user_id)
        if org_id:
            span.set_attribute("org_id", org_id)
        if request_id:
            span.set_attribute("request_id", request_id)
        
        start_time = time.time()
        
        try:
            yield
            
            duration_ms = (time.time() - start_time) * 1000
            request_counter.add(1, {"endpoint": endpoint, "method": method, "status": "success"})
            request_duration_histogram.record(duration_ms, {"endpoint": endpoint, "method": method})
            
            span.set_attribute("http.status_code", 200)
            
            # Alert on slow endpoints (>1000ms)
            if duration_ms > 1000:
                logger.warning(
                    f"Slow endpoint: {method} {endpoint} took {duration_ms:.2f}ms",
                    extra={"context": context}
                )
        
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            request_counter.add(1, {"endpoint": endpoint, "method": method, "status": "error"})
            request_duration_histogram.record(duration_ms, {"endpoint": endpoint, "method": method})
            errors_counter.add(1, {"endpoint": endpoint, "error_type": type(e).__name__})
            
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.set_attribute("http.status_code", 500)
            
            raise


def trace_operation(operation_name: str):
    """
    Decorator to trace a function as a named operation.
    
    Usage:
        @trace_operation("list_projects")
        def list_projects(auth, session):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            with time_operation(operation_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def record_db_operation(
    operation_type: str,
    table_name: str,
    count: int = 1,
):
    """
    Record a database operation metric.
    
    Args:
        operation_type: 'select', 'insert', 'update', 'delete'
        table_name: Name of the table
        count: Number of rows affected
    """
    db_query_counter.add(
        count,
        {"operation": operation_type, "table": table_name}
    )
    
    logger.debug(f"DB operation: {operation_type} on {table_name} ({count} rows)")


def record_error(
    error_type: str,
    context: Optional[Dict[str, Any]] = None,
):
    """
    Record an error for alerting.
    
    Args:
        error_type: Type of error (e.g., 'database_error', 'auth_error')
        context: Additional context about the error
    """
    attributes = {"error_type": error_type}
    if context:
        attributes.update(context)
    
    errors_counter.add(1, attributes)
    logger.error(f"Error recorded: {error_type}", extra={"context": context})


def get_request_summary() -> Dict[str, Any]:
    """Get summary of all operations in current request."""
    return _metrics_collector.get_request_summary()


def reset_request_metrics():
    """Reset metrics for the next request."""
    _metrics_collector.operations.clear()
    _metrics_collector.request_context.clear()
