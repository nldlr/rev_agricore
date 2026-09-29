from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Numeric, CheckConstraint
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import EquipmentStatus

if TYPE_CHECKING:
    from .farm import Farm
    from .field_job import FieldJob


class Equipment(Base):
    __tablename__ = "equipments"

    # Constraints
    __table_args__ = (
        CheckConstraint("fuel_level BETWEEN 0 and 100", name="fuel_level_range"),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    serial_number: Mapped[str] = mapped_column(String(50), unique=True)
    model: Mapped[str] = mapped_column(String(100))
    status: Mapped[EquipmentStatus] = mapped_column(SqlEnum(EquipmentStatus), name="equipment_status",
                                                     values_callable=lambda enum_cls: [member.value for member in enum_cls])
    fuel_level: Mapped[int] = mapped_column(Numeric(5, 2))
    farm_id: Mapped[int] = mapped_column(Integer, ForeignKey("farms.id"))

    # Relationships
    farm: Mapped["Farm"] = relationship(back_populates="equipments") # Each equipment has one farm.
    field_jobs: Mapped[list["FieldJob"]] = relationship(back_populates="equipment") # Each equipment has many field jobs.

    def __repr__(self) -> str:
            return f"Equipment(serial={self.serial_number!r}, Model={self.model!r}, Fuel Level={self.fuel_level}%, status={self.status.value})"
    