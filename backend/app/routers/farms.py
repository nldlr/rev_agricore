from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db, require_role
from app.models import Farm, FieldJob, FieldJobStatus, Operator, Farm, User, UserRole, Equipment, EquipmentStatus
from app.schemas.farm import MaintenanceFlag, OperatorActiveFieldJobs, ReportingLineResult, FarmRead, FarmCreate, FarmUpdate


router = APIRouter(prefix="/farms", tags=["farms"])

@router.get("", response_model=list[FarmRead]) # Response model = schema format that will be returned to the client.
async def list_farms(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user), # _ is for a variable you are required to define, but intend to ignore. Requires caller to be logged in with JWT token.
) -> list[Farm]:
    
    statement = select(Farm).order_by(Farm.id)

    result = await db.execute(statement) # Returns a list of database tuples: [(<Farm object>,), (<Farm object>,)]
    return list(result.scalars().all())


# POST /farms endpoint, creates a new farm.
@router.post("", response_model=FarmRead, status_code=status.HTTP_201_CREATED) # Returns 201 Created instead of standard 200
async def create_farm(payload: FarmCreate, db: AsyncSession = Depends(get_db), # Note the request schema.
    _: User = Depends(require_role(UserRole.FARM_OPERATIONS_ADMIN))) -> Farm:
    farm = Farm(**payload.model_dump()) # Converts validated Pydantic model into dictionary.
    db.add(farm) # Save to db.
    await db.commit()
    await db.refresh(farm)
    return farm

# UPDATE /farms/{farm_id} endpoint, update a single farm by ID.
@router.patch("/{farm_id}", response_model=FarmRead)
async def update_farm(
    farm_id: int,
    payload: FarmUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.FARM_OPERATIONS_ADMIN)),
) -> Farm:
    farm = await db.get(Farm, farm_id)
    if farm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm '{farm_id}' not found",
        )

    # Prepare updated values for copying.
    farm_updated = payload.model_dump(exclude_unset=True)

    # Update object with new values, if given.
    for field, value in farm_updated.items():
        setattr(farm, field, value)

    # Commit to database.
    await db.commit()
    await db.refresh(farm)
    return farm

# DELETE /farms endpoint, deletes an farm.
@router.delete("/{farm_id}", status_code=status.HTTP_204_NO_CONTENT) 
async def delete_farm(farm_id: int, db: AsyncSession = Depends(get_db), # Note the request schema.
    _: User = Depends(require_role(UserRole.FARM_OPERATIONS_ADMIN))) -> None:
    farm = await db.get(Farm, farm_id)
    if farm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm '{farm_id}' not found",
        )
    await db.delete(farm) # Needs await unlike .get() for some reason.
    await db.commit()
    return None

















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