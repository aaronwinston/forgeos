import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from database import get_session
from middleware.auth import AuthContext, get_current_user
from models import ContentEvalRun
from services.evaluation_harness import (
    BaselineSnapshot,
    DimensionScore,
    EvalResult,
    RegressionDelta,
    evaluate_workflow_artifact,
    parse_dimension_scores,
    parse_regression_deltas,
    serialize_dimension_scores,
    serialize_regression_deltas,
)

router = APIRouter(prefix="/api/evals", tags=["evals"])


class EvalRunRequest(BaseModel):
    workflow_type: str
    artifact_text: str = Field(min_length=1)
    artifact_key: str = Field(default="adhoc")
    prompt_version: Optional[str] = None
    skill_version: Optional[str] = None
    baseline_run_id: Optional[int] = None
    store_as_baseline: bool = False


class EvalRunResponse(BaseModel):
    run_id: int
    workflow_type: str
    artifact_key: str
    prompt_version: Optional[str] = None
    skill_version: Optional[str] = None
    gate_passed: bool
    overall_score: float
    failed_dimensions: list[str]
    dimension_scores: list[DimensionScore]
    regression_checked: bool
    regression_failed: bool
    regression_deltas: list[RegressionDelta]
    compared_to_run_id: Optional[int] = None


class EvalRunRecord(BaseModel):
    run_id: int
    workflow_type: str
    artifact_key: str
    overall_score: float
    gate_status: str
    regression_failed: bool
    is_baseline: bool



def _find_baseline_run(
    payload: EvalRunRequest,
    auth: AuthContext,
    session: Session,
) -> Optional[ContentEvalRun]:
    if payload.baseline_run_id is not None:
        baseline = session.exec(
            select(ContentEvalRun).where(
                (ContentEvalRun.id == payload.baseline_run_id)
                & (ContentEvalRun.organization_id == auth.org_id)
                & (ContentEvalRun.workflow_type == payload.workflow_type)
            )
        ).first()
        if not baseline:
            raise HTTPException(status_code=404, detail="Requested baseline_run_id not found")
        return baseline

    baseline = session.exec(
        select(ContentEvalRun)
        .where(
            (ContentEvalRun.organization_id == auth.org_id)
            & (ContentEvalRun.workflow_type == payload.workflow_type)
            & (ContentEvalRun.artifact_key == payload.artifact_key)
            & (ContentEvalRun.is_baseline == True)  # noqa: E712
        )
        .order_by(ContentEvalRun.created_at.desc(), ContentEvalRun.id.desc())
    ).first()
    if baseline:
        return baseline

    return session.exec(
        select(ContentEvalRun)
        .where(
            (ContentEvalRun.organization_id == auth.org_id)
            & (ContentEvalRun.workflow_type == payload.workflow_type)
            & (ContentEvalRun.artifact_key == payload.artifact_key)
        )
        .order_by(ContentEvalRun.created_at.desc(), ContentEvalRun.id.desc())
    ).first()


@router.post("/run", response_model=EvalRunResponse)
def run_content_eval(
    payload: EvalRunRequest,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if payload.workflow_type not in {"blog", "launch", "analyst"}:
        raise HTTPException(status_code=422, detail="Unsupported workflow_type")
    baseline_run = _find_baseline_run(payload=payload, auth=auth, session=session)
    baseline_snapshot = None
    if baseline_run:
        baseline_snapshot = BaselineSnapshot(
            run_id=baseline_run.id,
            dimension_scores=parse_dimension_scores(baseline_run.scores_json),
        )

    result: EvalResult = evaluate_workflow_artifact(
        workflow_type=payload.workflow_type,
        artifact_text=payload.artifact_text,
        baseline=baseline_snapshot,
    )

    record = ContentEvalRun(
        organization_id=auth.org_id,
        created_by_user_id=auth.user_id,
        workflow_type=payload.workflow_type,
        artifact_key=payload.artifact_key.strip() or "adhoc",
        artifact_text=payload.artifact_text,
        prompt_version=payload.prompt_version,
        skill_version=payload.skill_version,
        scores_json=serialize_dimension_scores(result.dimension_scores),
        overall_score=result.overall_score,
        gate_status="pass" if result.gate_passed else "fail",
        failed_dimensions_json=json.dumps(result.failed_dimensions, sort_keys=True),
        baseline_run_id=baseline_snapshot.run_id if baseline_snapshot else None,
        deltas_json=serialize_regression_deltas(result.regression_deltas),
        regression_failed=result.regression_failed,
        is_baseline=payload.store_as_baseline,
    )
    session.add(record)
    session.commit()
    session.refresh(record)

    return EvalRunResponse(
        run_id=record.id,
        workflow_type=record.workflow_type,
        artifact_key=record.artifact_key,
        prompt_version=record.prompt_version,
        skill_version=record.skill_version,
        gate_passed=result.gate_passed,
        overall_score=result.overall_score,
        failed_dimensions=result.failed_dimensions,
        dimension_scores=result.dimension_scores,
        regression_checked=result.regression_checked,
        regression_failed=result.regression_failed,
        regression_deltas=result.regression_deltas,
        compared_to_run_id=baseline_snapshot.run_id if baseline_snapshot else None,
    )


@router.get("/runs", response_model=list[EvalRunRecord])
def list_content_eval_runs(
    workflow_type: str,
    artifact_key: str = "adhoc",
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if workflow_type not in {"blog", "launch", "analyst"}:
        raise HTTPException(status_code=422, detail="Unsupported workflow_type")

    rows = session.exec(
        select(ContentEvalRun)
        .where(
            (ContentEvalRun.organization_id == auth.org_id)
            & (ContentEvalRun.workflow_type == workflow_type)
            & (ContentEvalRun.artifact_key == artifact_key)
        )
        .order_by(ContentEvalRun.created_at.desc(), ContentEvalRun.id.desc())
        .limit(50)
    ).all()

    return [
        EvalRunRecord(
            run_id=row.id,
            workflow_type=row.workflow_type,
            artifact_key=row.artifact_key,
            overall_score=row.overall_score,
            gate_status=row.gate_status,
            regression_failed=row.regression_failed,
            is_baseline=row.is_baseline,
        )
        for row in rows
    ]


@router.get("/runs/{run_id}", response_model=EvalRunResponse)
def get_content_eval_run(
    run_id: int,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    run = session.exec(
        select(ContentEvalRun).where(
            (ContentEvalRun.id == run_id) & (ContentEvalRun.organization_id == auth.org_id)
        )
    ).first()
    if not run:
        raise HTTPException(status_code=404, detail="Eval run not found")

    dimension_scores = parse_dimension_scores(run.scores_json)
    deltas = parse_regression_deltas(run.deltas_json or "[]")
    failed_dimensions = json.loads(run.failed_dimensions_json or "[]")

    return EvalRunResponse(
        run_id=run.id,
        workflow_type=run.workflow_type,
        artifact_key=run.artifact_key,
        prompt_version=run.prompt_version,
        skill_version=run.skill_version,
        gate_passed=run.gate_status == "pass",
        overall_score=run.overall_score,
        failed_dimensions=failed_dimensions,
        dimension_scores=dimension_scores,
        regression_checked=run.baseline_run_id is not None,
        regression_failed=run.regression_failed,
        regression_deltas=deltas,
        compared_to_run_id=run.baseline_run_id,
    )
