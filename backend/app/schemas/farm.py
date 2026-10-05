from pydantic import BaseModel, ConfigDict

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