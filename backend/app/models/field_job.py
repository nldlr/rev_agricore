from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import FieldJobPriority, FieldJobStatus

if TYPE_CHECKING:
    from .equipment import Equipment
    from .operator import Operator
    from .service_report import ServiceReport


class FieldJob(Base):
    __tablename__ = "field_jobs"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    priority: Mapped[FieldJobPriority] = mapped_column(SqlEnum(FieldJobPriority), name="field_job_priority",
                                                       values_callable=lambda enum_cls: [member.value for member in enum_cls])
    status: Mapped[FieldJobStatus] = mapped_column(SqlEnum(FieldJobStatus), name="field_job_status",
                                                   values_callable=lambda enum_cls: [member.value for member in enum_cls])
    equipment_id: Mapped[int] = mapped_column(Integer, ForeignKey("equipments.id"))
    operator_id: Mapped[int] = mapped_column(Integer, ForeignKey("operators.id"))

    # Relationships
    equipment: Mapped["Equipment"] = relationship(back_populates="field_jobs") # Each field job has one equipment.
    operator: Mapped["Operator"] = relationship(back_populates="field_jobs") # Each field job has one operator.
    service_reports: Mapped[list["ServiceReport"]] = relationship(back_populates="field_job") # Each field job has many service reports.

    def __repr__(self) -> str:
        return f"Field Job(id={self.id!r}, title={self.title!r}, priority={self.priority.value}, status={self.status.value})"