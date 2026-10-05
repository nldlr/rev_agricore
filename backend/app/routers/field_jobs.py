from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import select, case, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db, require_role
from app.models import FieldJob, FieldJobPriority, Operator, Equipment, FieldJobStatus, User, UserRole
from app.schemas.field_job import DiscrepancyRead, FieldJobRead, FieldJobStatusUpdate, ReliabilityMetric

router = APIRouter(prefix="/field_jobs", tags=["field_jobs"])

@router.get("", response_model=list[FieldJobRead]) # Response model = schema format that will be returned to the client.
async def list_field_jobs(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user), # _ is for a variable you are required to define, but intend to ignore. Requires caller to be logged in with JWT token.
) -> list[FieldJob]:
    
    statement = select(FieldJob).order_by(FieldJob.id)

    result = await db.execute(statement) # Returns a list of database tuples: [(<FieldJob object>,), (<FieldJob object>,)]
    return list(result.scalars().all())


@router.get("/discrepancies", response_model=list[DiscrepancyRead])
async def list_colocation_discrepancies(
    priority: FieldJobPriority | None = Query(
        default=None,
        description="Only return discrepancies for field jobs of this priority.",
    ),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.FARM_OPERATIONS_ADMIN, UserRole.FIELD_HAND)),
):
    """
    Business Question #2: Co-Location Discrepancy
    """
    statement = (
        select(
            FieldJob.id.label("field_job_id"),
            FieldJob.title,
            Equipment.farm_id.label("equipment_farm_id"),
            Operator.farm_id.label("operator_farm_id"),
        )
        .join(Equipment, Equipment.id == FieldJob.equipment_id)
        .join(Operator, Operator.id == FieldJob.operator_id)
        .where(Equipment.farm_id != Operator.farm_id)
    )

    # if a priority filter provided, add it to the WHERE clause
    if priority is not None:
        statement = statement.where(FieldJob.priority == priority)

    statement = statement.order_by(FieldJob.id)

    result = await db.execute(statement)
    return [dict(row) for row in result.mappings().all()]


@router.patch("/{field_job_id}/status", response_model=FieldJobRead)
async def update_field_job_status(
    field_job_id: int,
    payload: FieldJobStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.FARM_OPERATIONS_ADMIN, UserRole.FIELD_HAND)),
) -> FieldJob:
    field_job = await db.get(FieldJob, field_job_id)
    if field_job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"FieldJob '{field_job_id}' not found",
        )
    if payload.status == FieldJobStatus.COMPLETED:
        field_job.mark_completed()
    elif payload.status == FieldJobStatus.FAILED:
        field_job.mark_failed()
    else:
        field_job.status = payload.status

    await db.commit()
    await db.refresh(field_job)
    return field_job

@router.get("/reliability", response_model=list[ReliabilityMetric])
async def reliability_metrics(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Business Question #3: Reliability Metrics.
    Any authenticated role can view this - it's an analytics endpoint,
    matching the problem statement's "Auditor can view analytics
    dashboards" requirement, same as /missions/discrepancies.
    """
    statement = (
        select(
            Equipment.model,
            func.count(FieldJob.id).label("total_field_jobs"),
            func.sum(case((FieldJob.status == FieldJobStatus.COMPLETED, 1), else_=0)).label("completed_count"),
            func.sum(case((FieldJob.status == FieldJobStatus.FAILED, 1), else_=0)).label("failed_count"),
        )
        .join(FieldJob, FieldJob.equipment_id == Equipment.id)
        .group_by(Equipment.model)
        .order_by(Equipment.model)
    )
    result = await db.execute(statement)
    return [dict(row) for row in result.mappings().all()]