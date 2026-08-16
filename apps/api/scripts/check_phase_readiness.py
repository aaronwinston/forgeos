from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import sys


@dataclass(frozen=True)
class ReadinessSignal:
    description: str
    path: str
    contains: Optional[str] = None


REPO_ROOT = Path(__file__).resolve().parents[3]

PHASE_SIGNALS: dict[str, list[ReadinessSignal]] = {
    "Phase A - Foundation and hardening": [
        ReadinessSignal("Competitive POV context exists", "context/02_narrative/competitive-pov.md"),
        ReadinessSignal("Messaging framework exists", "context/02_narrative/messaging-framework.md"),
        ReadinessSignal("Claims policy exists", "core/CLAIMS_POLICY.md"),
        ReadinessSignal("Auth router exists", "apps/api/routers/auth.py"),
        ReadinessSignal("Auth tests exist", "apps/api/tests/test_auth.py"),
        ReadinessSignal("Security tests exist", "apps/api/tests/test_security.py"),
    ],
    "Phase B - Publishing and execution": [
        ReadinessSignal("WordPress publishing service exists", "apps/api/services/x_to_wordpress.py"),
        ReadinessSignal(
            "Publishing endpoint is wired",
            "apps/api/routers/x_to_wordpress.py",
            '"/x-to-wordpress"',
        ),
        ReadinessSignal("Projects router exists", "apps/api/routers/projects.py"),
        ReadinessSignal("Publishing tests exist", "apps/api/tests/test_publishing.py"),
        ReadinessSignal("Project workflow tests exist", "apps/api/tests/test_projects.py"),
    ],
    "Phase C - Growth loops (SEO + intelligence)": [
        ReadinessSignal("SEO recommendations service exists", "apps/api/services/seo_recommendations.py"),
        ReadinessSignal("GSC integration service exists", "apps/api/services/gsc.py"),
        ReadinessSignal("Trends service exists", "apps/api/services/trends.py"),
        ReadinessSignal(
            "Search recommendations endpoint exists",
            "apps/api/routers/intelligence.py",
            '"/search/recommendations"',
        ),
        ReadinessSignal(
            "Planning queue endpoint exists",
            "apps/api/routers/intelligence.py",
            '"/planning/queue"',
        ),
        ReadinessSignal("SEO recommendation tests exist", "apps/api/tests/test_seo_recommendations.py"),
        ReadinessSignal(
            "Planning queue tests exist",
            "apps/api/tests/test_intelligence_planning_queue.py",
        ),
    ],
    "Phase D - AI quality and distribution scale": [
        ReadinessSignal("Eval harness service exists", "apps/api/services/evaluation_harness.py"),
        ReadinessSignal("Evals API router exists", "apps/api/routers/evals.py"),
        ReadinessSignal(
            "Evals run endpoint exists",
            "apps/api/routers/evals.py",
            '"/run"',
        ),
        ReadinessSignal("Instrumentation module exists", "apps/api/instrumentation.py"),
        ReadinessSignal("Eval harness tests exist", "apps/api/tests/test_eval_harness.py"),
        ReadinessSignal(
            "Distribution integration tests exist",
            "apps/api/tests/test_distribution_integrations.py",
        ),
    ],
}


def _check_signal(signal: ReadinessSignal, repo_root: Path) -> tuple[bool, str]:
    target = repo_root / signal.path
    if not target.exists():
        return False, f"missing file: {signal.path}"
    if signal.contains:
        text = target.read_text(encoding="utf-8")
        if signal.contains not in text:
            return False, f"missing token `{signal.contains}` in {signal.path}"
    return True, "ok"


def evaluate_readiness(
    phase_signals: dict[str, list[ReadinessSignal]], repo_root: Path
) -> tuple[list[str], dict[str, tuple[int, int]]]:
    failures: list[str] = []
    summaries: dict[str, tuple[int, int]] = {}
    for phase, signals in phase_signals.items():
        passed = 0
        for signal in signals:
            success, detail = _check_signal(signal, repo_root)
            if success:
                passed += 1
            else:
                failures.append(f"{phase}: {signal.description} ({detail})")
        summaries[phase] = (passed, len(signals))
    return failures, summaries


def main() -> int:
    failures, summaries = evaluate_readiness(PHASE_SIGNALS, REPO_ROOT)
    print("ForgeOS phased rollout readiness")
    for phase, (passed, total) in summaries.items():
        status = "PASS" if passed == total else "FAIL"
        print(f"- {status} {phase}: {passed}/{total}")

    if failures:
        print("\nGo/No-Go result: NO-GO")
        print("Blocking signals:")
        for issue in failures:
            print(f"  - {issue}")
        return 1

    print("\nGo/No-Go result: GO")
    print("All required phase signals are present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
