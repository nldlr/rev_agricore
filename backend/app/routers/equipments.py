from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user, require_role
from app.models import Equipment, EquipmentStatus, User, UserRole
from app.schemas.equipment import EquipmentCreate, EquipmentRead


# Every route will start with /equipments. Tags categorizes these routes under "equipments" heading in SwaggerUI. (/docs)
router = APIRouter(prefix="/equipments", tags=["equipments"])

# Request schemas can come from path parameters, query parameters, or the payload (JSON Request Body).

# GET /equipment endpoint, returns a list of equipment, optionally filtered by fuel level.
@router.get("", response_model=list[EquipmentRead]) # Response model = schema format that will be returned to the client.
async def list_equipments( # Request schema is defined inside the function's parameter signature here.
    max_fuel: Decimal | None = Query( # Optional Query Parameter, captures ?max_fuel=20.0 from URL, and ge/le validates it.
        default=None,
        ge=0,
        le=100,
        description="Only return equipment strictly below this fuel level.",
    ),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user), # _ is for a variable you are required to define, but intend to ignore. Requires caller to be logged in with JWT token.
) -> list[Equipment]:
    """
    Business Question #1: Low Fuel Alert
    """
    
    statement = select(Equipment).where(Equipment.status != EquipmentStatus.RETIRED)
    if max_fuel is not None:
        statement = statement.where(Equipment.fuel_level < max_fuel)
    statement = statement.order_by(Equipment.id)

    result = await db.execute(statement) # Returns a list of database tuples: [(<Equipment object>,), (<Equipment object>,)]
    return list(result.scalars().all()) # .scalars() unwraps it for first col value: [<Equipment object>, <Equipment object>]
    # Then .all() loads all items into standard python list: [Equipment, Equipment]

# GET /equipments/{equipment_id} endpoint, returns a single equipment by ID.
@router.get("/{equipment_id}", response_model=EquipmentRead)
async def get_equipment(equipment_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)) -> Equipment:
    # Equipment id captured via path parameter. Requires a valid logged-in users.
    equipment = await db.get(Equipment, equipment_id)
    if equipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipment {equipment_id} not found",
        )
    return equipment

# POST /equipments endpoint, creates a new equipment.
@router.post("", response_model=EquipmentRead, status_code=status.HTTP_201_CREATED) # Returns 201 Created instead of standard 200
async def create_equipment(payload: EquipmentCreate, db: AsyncSession = Depends(get_db), # Note the request schema.
    _: User = Depends(require_role(UserRole.FARM_OPERATIONS_ADMIN))) -> Equipment:
    equipment = Equipment(**payload.model_dump()) # Converts validated Pydantic model into dictionary.
    db.add(equipment) # Save to db.
    await db.commit()
    await db.refresh(equipment)
    return equipment