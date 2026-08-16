from scripts.check_phase_readiness import (
    PHASE_SIGNALS,
    REPO_ROOT,
    ReadinessSignal,
    evaluate_readiness,
)


def test_phase_readiness_signals_pass_for_current_repo():
    failures, summaries = evaluate_readiness(PHASE_SIGNALS, REPO_ROOT)
    assert failures == []
    assert all(passed == total for passed, total in summaries.values())


def test_phase_readiness_reports_missing_file():
    custom_signals = {
        "Phase X": [ReadinessSignal("Missing test artifact", "apps/api/tests/does_not_exist.py")]
    }
    failures, summaries = evaluate_readiness(custom_signals, REPO_ROOT)
    assert len(failures) == 1
    assert "missing file" in failures[0]
    assert summaries["Phase X"] == (0, 1)
