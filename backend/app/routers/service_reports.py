from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import select, case, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db, require_role
from app.models import FieldJob, FieldJobPriority, Operator, ServiceReport, FieldJobStatus, User, UserRole
from app.schemas.field_job import DiscrepancyRead, FieldJobRead, FieldJobStatusUpdate, ReliabilityMetric
from app.schemas.service_report import ServiceReportRead, ServiceReportCreate, ServiceReportUpdate

router = APIRouter(prefix="/service_reports", tags=["service_reports"])

@router.get("", response_model=list[ServiceReportRead]) # Response model = schema format that will be returned to the client.
async def list_service_reports(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user), # _ is for a variable you are required to define, but intend to ignore. Requires caller to be logged in with JWT token.
) -> list[ServiceReport]:
    
    statement = select(ServiceReport).order_by(ServiceReport.id)

    result = await db.execute(statement) # Returns a list of database tuples: [(<ServiceReport object>,), (<ServiceReport object>,)]
    return list(result.scalars().all()) # .scalars() unwraps it for first col value: [<ServiceReport object>, <ServiceReport object>]
    # Then .all() loads all items into standard python list: [ServiceReport, ServiceReport]

# POST /service_reports endpoint, creates a new service_report.
@router.post("", response_model=ServiceReportCreate, status_code=status.HTTP_201_CREATED) # Returns 201 Created instead of standard 200
async def create_service_report(payload: ServiceReportCreate, db: AsyncSession = Depends(get_db), # Note the request schema.
    _: User = Depends(require_role(UserRole.FARM_OPERATIONS_ADMIN, UserRole.FIELD_HAND))) -> ServiceReport:
    service_report = ServiceReport(**payload.model_dump()) # Converts validated Pydantic model into dictionary.
    db.add(service_report) # Save to db.
    await db.commit()
    await db.refresh(service_report)
    return service_report


# UPDATE /service_reports/{service_report_id} endpoint, update a single service_report by ID.
@router.patch("/{service_report_id}", response_model=ServiceReportRead)
async def update_service_report(
    service_report_id: int,
    payload: ServiceReportUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.FARM_OPERATIONS_ADMIN)),
) -> ServiceReport:
    service_report = await db.get(ServiceReport, service_report_id)
    if service_report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ServiceReport '{service_report_id}' not found",
        )

    # Prepare updated values for copying.
    service_report_updated = payload.model_dump(exclude_unset=True)

    # Update object with new values, if given.
    for field, value in service_report_updated.items():
        setattr(service_report, field, value)

    # Commit to database.
    await db.commit()
    await db.refresh(service_report)
    return service_report

# DELETE /service_reports endpoint, deletes an service_report.
@router.delete("/{service_report_id}", status_code=status.HTTP_204_NO_CONTENT) 
async def delete_service_report(service_report_id: int, db: AsyncSession = Depends(get_db), # Note the request schema.
    _: User = Depends(require_role(UserRole.FARM_OPERATIONS_ADMIN))) -> None:
    service_report = await db.get(ServiceReport, service_report_id)
    if service_report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ServiceReport '{service_report_id}' not found",
        )
    await db.delete(service_report) # Needs await unlike .get() for some reason.
    await db.commit()
    return None