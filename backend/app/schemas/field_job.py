from pydantic import BaseModel, ConfigDict

from app.models.enums import FieldJobPriority, FieldJobStatus

class FieldJobStatusUpdate(BaseModel):
    status: FieldJobStatus


class FieldJobRead(BaseModel):
    id: int
    title: str
    priority: FieldJobPriority
    status: FieldJobStatus
    equipment_id: int
    operator_id: int

    model_config = ConfigDict(from_attributes=True)




class DiscrepancyRead(BaseModel):
    field_job_id: int
    title: str
    equipment_farm_id: int
    operator_farm_id: int
    model_config = ConfigDict(from_attributes=True)


class ReliabilityMetric(BaseModel):
    model: str
    total_field_jobs: int
    completed_count: int
    failed_count: int
