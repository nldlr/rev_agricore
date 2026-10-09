from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import EquipmentStatus

class AuditBase(BaseModel):
    # id: Mapped[int] = mapped_column(primary_key=True)
    #     user_id: Mapped[int] = mapped_column(Integer)
    #     action: Mapped[str] = mapped_column(String(255))
    #     entity_type: Mapped[str] = mapped_column(String(255))
    #     entity_id: Mapped[int] = mapped_column(Integer)
    
    user_id: int
    action: str = Field(min_length=1, max_length=255) # DELETE
    entity_type: str = Field(min_length=1, max_length=255) # USER
    entity_id: int

class AuditRead(AuditBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class AuditCreate(AuditBase):
    pass