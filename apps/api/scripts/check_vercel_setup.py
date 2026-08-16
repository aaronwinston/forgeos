#!/usr/bin/env python3
"""Validate ForgeOS Vercel deployment configuration."""

from __future__ import annotations

from pathlib import Path
import sys


def check(condition: bool, ok_msg: str, fail_msg: str, failures: list[str]) -> None:
    if condition:
        print(f"OK   {ok_msg}")
    else:
        print(f"FAIL {fail_msg}")
        failures.append(fail_msg)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[3]
    failures: list[str] = []

    web_vercel_json = repo_root / "apps" / "web" / "vercel.json"
    root_vercel_json = repo_root / "vercel.json"
    web_next_config = repo_root / "apps" / "web" / "next.config.mjs"
    deploy_workflow = repo_root / ".github" / "workflows" / "deploy.yml"
    api_env_example = repo_root / "apps" / "api" / ".env.example"
    root_env_example = repo_root / ".env.example"

    check(
        web_vercel_json.exists(),
        "apps/web/vercel.json exists",
        "apps/web/vercel.json is missing",
        failures,
    )
    check(
        not root_vercel_json.exists(),
        "repo root vercel.json removed to avoid root/apps-web ambiguity",
        "repo root vercel.json still exists (ambiguous Vercel root config)",
        failures,
    )

    next_config_text = web_next_config.read_text(encoding="utf-8") if web_next_config.exists() else ""
    check(
        web_next_config.exists(),
        "apps/web/next.config.mjs exists",
        "apps/web/next.config.mjs is missing",
        failures,
    )
    check(
        "output: 'export'" not in next_config_text and 'output: "export"' not in next_config_text,
        "apps/web/next.config.mjs is configured for dynamic runtime",
        "apps/web/next.config.mjs still enables static export mode",
        failures,
    )

    workflow_text = deploy_workflow.read_text(encoding="utf-8") if deploy_workflow.exists() else ""
    check(
        deploy_workflow.exists(),
        ".github/workflows/deploy.yml exists",
        ".github/workflows/deploy.yml is missing",
        failures,
    )
    check(
        "workflow_dispatch" in workflow_text and "push:" not in workflow_text,
        "deploy workflow is manual-only (no automatic GitHub Pages conflict)",
        "deploy workflow still auto-triggers on push",
        failures,
    )

    api_env_text = api_env_example.read_text(encoding="utf-8") if api_env_example.exists() else ""
    root_env_text = root_env_example.read_text(encoding="utf-8") if root_env_example.exists() else ""
    check(
        "CORS_ALLOWED_ORIGINS" in api_env_text,
        "apps/api/.env.example contains CORS_ALLOWED_ORIGINS",
        "apps/api/.env.example missing CORS_ALLOWED_ORIGINS",
        failures,
    )
    check(
        "NEXT_PUBLIC_API_BASE_URL" in root_env_text,
        ".env.example contains NEXT_PUBLIC_API_BASE_URL",
        ".env.example missing NEXT_PUBLIC_API_BASE_URL",
        failures,
    )

    if failures:
        print(f"\nVercel setup check: NO-GO ({len(failures)} issue(s))")
        return 1

    print("\nVercel setup check: GO")
    return 0


if __name__ == "__main__":
    sys.exit(main())
