from middleware.auth import AuthContext
from routers.evals import EvalRunRequest, get_content_eval_run, run_content_eval
from services.evaluation_harness import (
    BaselineSnapshot,
    WORKFLOW_DIMENSIONS,
    evaluate_workflow_artifact,
)


def _strong_blog_artifact() -> str:
    return """
## Why eval gates fail in production

Teams usually start by watching traces, then they realize a trace alone does not prove quality.
A reliable loop needs a rubric, a benchmark set, and a regression gate before rollout.

### Concrete workflow

1. Capture traces for the same prompt, retrieval path, and tool call pattern.
2. Score each run against editorial quality, technical accuracy, developer fluency, and brand fit.
3. Record failures by failure mode: retrieval miss, tool timeout, stale context, or unsafe claim.
4. Compare the new prompt version against a baseline snapshot and block release on regressions.

This workflow is useful because it explains tradeoffs. A stricter gate catches claims risk
but may slow release velocity, so the team documents the limitation and adjusts the threshold.
The API can return per-dimension scores, reasons, and a pass or fail decision. Engineers can
review deltas, inspect trace evidence, and decide whether the prompt change improved quality.
""".strip()


def test_evaluate_workflow_artifact_blog_dimensions_and_gate_passes():
    result = evaluate_workflow_artifact("blog", _strong_blog_artifact())

    assert result.gate_passed is True
    assert [score.dimension for score in result.dimension_scores] == WORKFLOW_DIMENSIONS["blog"]
    assert all(score.score >= 4 for score in result.dimension_scores)


def test_evaluate_workflow_artifact_launch_flags_claims_risk():
    risky_launch_text = (
        "Our revolutionary launch is the best in the market and 70% faster than alternatives. "
        "This is guaranteed to transform every team."
    )

    result = evaluate_workflow_artifact("launch", risky_launch_text)

    claims_risk = [score for score in result.dimension_scores if score.dimension == "claims_risk"][0]
    assert claims_risk.score < 4
    assert result.gate_passed is False
    assert "claims_risk" in result.failed_dimensions


def test_evaluate_workflow_artifact_regression_detection():
    baseline_result = evaluate_workflow_artifact("blog", _strong_blog_artifact())
    baseline = BaselineSnapshot(run_id=10, dimension_scores=baseline_result.dimension_scores)

    regressed_text = "Excited to announce a powerful next-generation platform that changes everything."
    result = evaluate_workflow_artifact("blog", regressed_text, baseline=baseline)

    assert result.regression_checked is True
    assert result.regression_failed is True
    assert any(delta.delta <= -1 for delta in result.regression_deltas)


def test_run_content_eval_persists_and_compares_with_baseline(test_session, test_user):
    user_id, org_id = test_user
    auth = AuthContext(user_id=user_id, org_id=org_id, role="member")

    baseline_response = run_content_eval(
        payload=EvalRunRequest(
            workflow_type="blog",
            artifact_text=_strong_blog_artifact(),
            artifact_key="artifact-1",
            prompt_version="prompt:v1",
            skill_version="skill:v1",
            store_as_baseline=True,
        ),
        auth=auth,
        session=test_session,
    )
    assert baseline_response.gate_passed is True

    second_response = run_content_eval(
        payload=EvalRunRequest(
            workflow_type="blog",
            artifact_text="Delighted to share the best platform ever.",
            artifact_key="artifact-1",
            prompt_version="prompt:v2",
            skill_version="skill:v1",
        ),
        auth=auth,
        session=test_session,
    )

    assert second_response.compared_to_run_id == baseline_response.run_id
    assert second_response.regression_failed is True
    assert second_response.gate_passed is False

    fetched = get_content_eval_run(
        run_id=second_response.run_id,
        auth=auth,
        session=test_session,
    )
    assert fetched.compared_to_run_id == baseline_response.run_id
    assert fetched.regression_failed is True
