from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import select, case, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db, require_role
from app.models import FieldJob, FieldJobPriority, Operator, Equipment, FieldJobStatus, User, UserRole
from app.schemas.field_job import DiscrepancyRead, FieldJobRead, FieldJobStatusUpdate, ReliabilityMetric, FieldJobUpdate, FieldJobCreate

router = APIRouter(prefix="/field_jobs", tags=["field_jobs"])

@router.get("", response_model=list[FieldJobRead]) # Response model = schema format that will be returned to the client.
async def list_field_jobs(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user), # _ is for a variable you are required to define, but intend to ignore. Requires caller to be logged in with JWT token.
) -> list[FieldJob]:
    
    statement = select(FieldJob).order_by(FieldJob.id)

    result = await db.execute(statement) # Returns a list of database tuples: [(<FieldJob object>,), (<FieldJob object>,)]
    return list(result.scalars().all())

# POST /field_jobs endpoint, creates a new field_job.
@router.post("", response_model=FieldJobRead, status_code=status.HTTP_201_CREATED) # Returns 201 Created instead of standard 200
async def create_field_job(payload: FieldJobCreate, db: AsyncSession = Depends(get_db), # Note the request schema.
    _: User = Depends(require_role(UserRole.FARM_OPERATIONS_ADMIN))) -> FieldJob:
    field_job = FieldJob(**payload.model_dump()) # Converts validated Pydantic model into dictionary.
    db.add(field_job) # Save to db.
    await db.commit()
    await db.refresh(field_job)
    return field_job

# UPDATE /field_jobs/{field_job_id} endpoint, update a single field_job by ID.
@router.patch("/{field_job_id}", response_model=FieldJobRead)
async def update_field_job(
    field_job_id: int,
    payload: FieldJobUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.FARM_OPERATIONS_ADMIN)),
) -> FieldJob:
    field_job = await db.get(FieldJob, field_job_id)
    if field_job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"FieldJob '{field_job_id}' not found",
        )

    # Prepare updated values for copying.
    field_job_updated = payload.model_dump(exclude_unset=True)

    # Update object with new values, if given.
    for field, value in field_job_updated.items():
        setattr(field_job, field, value)

    # Commit to database.
    await db.commit()
    await db.refresh(field_job)
    return field_job

# DELETE /field_jobs endpoint, deletes an field_job.
@router.delete("/{field_job_id}", status_code=status.HTTP_204_NO_CONTENT) 
async def delete_field_job(field_job_id: int, db: AsyncSession = Depends(get_db), # Note the request schema.
    _: User = Depends(require_role(UserRole.FARM_OPERATIONS_ADMIN))) -> None:
    field_job = await db.get(FieldJob, field_job_id)
    if field_job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"FieldJob '{field_job_id}' not found",
        )
    await db.delete(field_job) # Needs await unlike .get() for some reason.
    await db.commit()
    return None












@router.get("/discrepancies", response_model=list[DiscrepancyRead])
async def list_colocation_discrepancies(
    priority: FieldJobPriority | None = Query(
        default=None,
        description="Only return discrepancies for field jobs of this priority.",
    ),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.FARM_OPERATIONS_ADMIN, UserRole.FIELD_HAND, UserRole.AUDITOR)),
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