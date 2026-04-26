"""
ForgeOS — Arize AX tracing instrumentation.

Import this module at the very top of main.py (before any Anthropic clients
are created) so the instrumentor patches the SDK globally.

Required environment variables (set in .env):
  ARIZE_SPACE_ID  — from app.arize.com/organizations/-/settings/space-api-keys
  ARIZE_API_KEY   — same page

Optional:
  ARIZE_PROJECT_NAME — defaults to "forgeos"
"""

import os
import logging

logger = logging.getLogger(__name__)

_tracer_provider = None


def setup_tracing():
    """Register Arize OTel and instrument the Anthropic SDK. Call once at startup."""
    global _tracer_provider

    space_id = os.environ.get("ARIZE_SPACE_ID", "")
    api_key = os.environ.get("ARIZE_API_KEY", "")
    project_name = os.environ.get("ARIZE_PROJECT_NAME", "forgeos")

    if not space_id or not api_key:
        logger.warning(
            "Arize tracing disabled: ARIZE_SPACE_ID and/or ARIZE_API_KEY not set. "
            "Add them to apps/api/.env to enable observability."
        )
        return None

    try:
        from arize.otel import register
        from openinference.instrumentation.anthropic import AnthropicInstrumentor

        tracer_provider = register(
            space_id=space_id,
            api_key=api_key,
            project_name=project_name,
        )

        AnthropicInstrumentor().instrument(tracer_provider=tracer_provider)

        _tracer_provider = tracer_provider
        logger.info(f"Arize tracing enabled — project: {project_name}")
        return tracer_provider

    except Exception as e:
        logger.warning(f"Arize tracing setup failed (non-fatal): {e}")
        return None


def get_tracer():
    """Return an OTel tracer for manual CHAIN spans. Safe to call even if tracing is disabled."""
    try:
        from opentelemetry import trace
        return trace.get_tracer("forgeos", "1.0.0")
    except Exception:
        return None
