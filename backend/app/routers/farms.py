from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models import Farm, FieldJob, FieldJobStatus, Operator, Equipment, EquipmentStatus, User
from app.schemas.farm import MaintenanceFlag, OperatorActiveFieldJobs, ReportingLineResult, FarmRead

router = APIRouter(prefix="/farms", tags=["farms"])

@router.get("", response_model=list[FarmRead]) # Response model = schema format that will be returned to the client.
async def list_farms(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user), # _ is for a variable you are required to define, but intend to ignore. Requires caller to be logged in with JWT token.
) -> list[Farm]:
    
    statement = select(Farm).order_by(Farm.id)

    result = await db.execute(statement) # Returns a list of database tuples: [(<Farm object>,), (<Farm object>,)]
    return list(result.scalars().all())


@router.get("/maintenance-flags", response_model=list[MaintenanceFlag])
async def maintenance_flags(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Business Question #4: Maintenance Flags.

    WHERE filters rows BEFORE they're grouped/aggregated; this
    question needs to filter on a value that only exists AFTER
    aggregation (a computed percentage per Farm) - that's exactly
    what HAVING is for, and it's the first HAVING clause anywhere in
    this project.
    """
    maintenance_count = func.sum(case((Equipment.status == EquipmentStatus.MAINTENANCE, 1), else_=0))
    total_equipments = func.count(Equipment.id)
    maintenance_pct = maintenance_count * 100.0 / total_equipments

    statement = (
        select(
            Farm.id.label("farm_id"),
            Farm.name.label("farm_name"),
            total_equipments.label("total_equipments"),
            maintenance_count.label("maintenance_count"),
            maintenance_pct.label("maintenance_percentage"),
        )
        .join(Equipment, Equipment.farm_id == Farm.id)
        .group_by(Farm.id, Farm.name)
        .having(maintenance_pct > 30)
        .order_by(Farm.id)
    )
    result = await db.execute(statement)
    return [dict(row) for row in result.mappings().all()]


@router.get("/reporting-lines", response_model=ReportingLineResult)
async def reporting_lines(
    supervisor_id: int = Query(..., description="Regional Supervisor's ID (Farm.supervisor_id)."),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Business Question #5: Reporting Lines.

    "Active" mirrors the same definition used everywhere else in this
    project: not yet Completed or Failed - i.e. Pending or
    In-Progress. supervisor_id is deliberately a query parameter, not
    a path parameter tied to a real resource - Day 2's schema.sql
    never modeled supervisors/employees as their own table, so
    supervisor_id is just a plain integer on Farm with nothing to
    look up by ID.
    """
    statement = (
        select(
            Operator.id.label("operator_id"),
            Operator.name.label("operator_name"),
            func.count(FieldJob.id).label("active_field_job_count"),
        )
        .join(Farm, Farm.id == Operator.farm_id)
        .join(FieldJob, FieldJob.operator_id == Operator.id)
        .where(
            Farm.supervisor_id == supervisor_id,
            FieldJob.status.in_([FieldJobStatus.PENDING, FieldJobStatus.IN_PROGRESS]),
        )
        .group_by(Operator.id, Operator.name)
        .order_by(Operator.id)
    )
    result = await db.execute(statement)
    operators = [OperatorActiveFieldJobs(**row) for row in result.mappings().all()]

    return ReportingLineResult(
        supervisor_id=supervisor_id,
        operator_count=len(operators),
        operators=operators,
    )