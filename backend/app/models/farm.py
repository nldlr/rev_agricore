from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .equipment import Equipment
    from .operator import Operator
    

class Farm(Base):
    __tablename__ = "farms"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    location_region: Mapped[str] = mapped_column(String(50))
    capacity: Mapped[int] = mapped_column(Integer)
    supervisor_id: Mapped[int] = mapped_column(Integer)

    # Relationships
    equipments: Mapped[list["Equipment"]] = relationship(back_populates="farm") # Each farm has many equipments.
    operators: Mapped[list["Operator"]] = relationship(back_populates="farm") # Each farm has many operators.

    def __repr__(self) -> str:
        return (f"Farm(id={self.id!r}, Name={self.name!r}, Capacity={self.capacity}%, Supervisor Id={self.supervisor_id})")