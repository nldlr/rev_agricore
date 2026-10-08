from pydantic import BaseModel, ConfigDict
from typing import Optional

class FarmRead(BaseModel):
    # id: Mapped[int] = mapped_column(primary_key=True)
    #     name: Mapped[str] = mapped_column(String(100))
    #     location_region: Mapped[str] = mapped_column(String(50))
    #     capacity: Mapped[int] = mapped_column(Integer)
    #     supervisor_id: Mapped[int] = mapped_column(Integer)
    id: int
    name: str
    location_region: str
    capacity: int
    supervisor_id: int
    model_config = ConfigDict(from_attributes=True)

class FarmCreate(BaseModel):
    name: str
    location_region: str
    capacity: int
    supervisor_id: int

class FarmUpdate(BaseModel):
    # id would be provided as a path parameter, not in the JSON request body
    # everything else is an optional field
    name: Optional[str] = None
    location_region: Optional[str] = None
    capacity: Optional[int] = None
    supervisor_id: Optional[int] = None

class MaintenanceFlag(BaseModel):
    farm_id: int
    farm_name: str
    total_equipments: int
    maintenance_count: int
    maintenance_percentage: float

class OperatorActiveFieldJobs(BaseModel):
    operator_id: int
    operator_name: str
    active_field_job_count: int

class ReportingLineResult(BaseModel):
    supervisor_id: int
    operator_count: int
    operators: list[OperatorActiveFieldJobs]