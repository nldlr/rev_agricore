from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models import Audit
from app.schemas.audit import AuditRead, AuditCreate

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db, require_role
from app.models import Farm, FieldJob, FieldJobStatus, Operator, Farm, User, UserRole, Equipment, EquipmentStatus
from app.schemas.farm import MaintenanceFlag, OperatorActiveFieldJobs, ReportingLineResult, FarmRead, FarmCreate, FarmUpdate

router = APIRouter(prefix="/audits", tags=["audits"])

@router.get("", response_model=list[AuditRead]) # Response model = schema format that will be returned to the client.
async def list_audits(
    db: AsyncSession = Depends(get_db),
    _: Audit = Depends(get_current_user), # _ is for a variable you are required to define, but intend to ignore. Requires caller to be logged in with JWT token.
) -> list[Audit]:
    
    statement = select(Audit).order_by(Audit.id)

    result = await db.execute(statement)
    return list(result.scalars().all())

# POST /audits endpoint, creates a new audit.
@router.post("", response_model=AuditRead, status_code=status.HTTP_201_CREATED) # Returns 201 Created instead of standard 200
async def create_audit(payload: AuditCreate, db: AsyncSession = Depends(get_db), # Note the request schema.
    _: User = Depends(require_role(UserRole.FARM_OPERATIONS_ADMIN))) -> Audit:
    audit = Audit(**payload.model_dump()) # Converts validated Pydantic model into dictionary.
    db.add(audit) # Save to db.
    await db.commit()
    await db.refresh(audit)
    return audit