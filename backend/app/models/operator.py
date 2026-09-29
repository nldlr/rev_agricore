from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .farm import Farm
    from .field_job import FieldJob


class Operator(Base):
    __tablename__ = "operators"
    id: Mapped[int] = mapped_column(primary_key=True)
    farm_id: Mapped[int] = mapped_column(Integer, ForeignKey("farms.id"))
    name: Mapped[str] = mapped_column(String(100))

    # Relationships
    farm: Mapped["Farm"] = relationship(back_populates="operators") # Each operator has one farm.
    field_jobs: Mapped[list["FieldJob"]] = relationship(back_populates="operator") # Each operator has many field jobs.
    
    def __repr__(self) -> str:
        return f"Operator(id={self.id!r}, farm_id={self.farm_id}, name={self.name!r})"