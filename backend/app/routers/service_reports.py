from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import select, case, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db, require_role
from app.models import FieldJob, FieldJobPriority, Operator, ServiceReport, FieldJobStatus, User, UserRole
from app.schemas.field_job import DiscrepancyRead, FieldJobRead, FieldJobStatusUpdate, ReliabilityMetric
from app.schemas.service_report import ServiceReportRead, ServiceReportCreate

router = APIRouter(prefix="/service_reports", tags=["service_reports"])


@router.get("", response_model=list[ServiceReportRead]) # Response model = schema format that will be returned to the client.
async def list_equipments(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user), # _ is for a variable you are required to define, but intend to ignore. Requires caller to be logged in with JWT token.
) -> list[ServiceReport]:
    
    statement = select(ServiceReport).order_by(ServiceReport.id)

    result = await db.execute(statement) # Returns a list of database tuples: [(<ServiceReport object>,), (<ServiceReport object>,)]
    return list(result.scalars().all()) # .scalars() unwraps it for first col value: [<ServiceReport object>, <ServiceReport object>]
    # Then .all() loads all items into standard python list: [ServiceReport, ServiceReport]

# POST /equipments endpoint, creates a new equipment.
@router.post("", response_model=ServiceReportCreate, status_code=status.HTTP_201_CREATED) # Returns 201 Created instead of standard 200
async def create_equipment(payload: ServiceReportCreate, db: AsyncSession = Depends(get_db), # Note the request schema.
    _: User = Depends(require_role(UserRole.FARM_OPERATIONS_ADMIN, UserRole.FIELD_HAND))) -> ServiceReport:
    equipment = ServiceReport(**payload.model_dump()) # Converts validated Pydantic model into dictionary.
    db.add(equipment) # Save to db.
    await db.commit()
    await db.refresh(equipment)
    return equipment