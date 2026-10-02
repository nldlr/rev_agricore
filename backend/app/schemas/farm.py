from pydantic import BaseModel


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