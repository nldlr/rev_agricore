import pytest_asyncio

from app.models import FieldJob, FieldJobPriority, FieldJobStatus, Operator, Equipment, EquipmentStatus
from tests.conftest import auth_header

@pytest_asyncio.fixture
async def seeded_field_job(db_session, seeded_farm):
    equipment = Equipment(
        serial_number="MX-0001",
        model="Test-Equipment",
        status=EquipmentStatus.IDLE,
        fuel_level=75,
        farm_id=seeded_farm.id,
    )
    operator = Operator(name="Test Operator", farm_id=seeded_farm.id)
    db_session.add_all([equipment, operator])
    await db_session.commit()
    await db_session.refresh(equipment)
    await db_session.refresh(operator)

    field_job = FieldJob(
        title="Test Field Job",
        priority=FieldJobPriority.LOW,
        status=FieldJobStatus.PENDING,
        equipment_id=equipment.id,
        operator_id=operator.id,
    )
    db_session.add(field_job)
    await db_session.commit()
    await db_session.refresh(field_job)
    return field_job

async def test_clinical_admin_can_update_status(client, seeded_users, seeded_field_job):
    response = await client.patch(
        f"/field_jobs/{seeded_field_job.id}/status",
        json={"status": "Completed"},
        headers=auth_header(seeded_users["admin"]),
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Completed"

async def test_field_hand_can_update_status(client, seeded_users, seeded_field_job):
    response = await client.patch(
        f"/field_jobs/{seeded_field_job.id}/status",
        json={"status": "Failed"},
        headers=auth_header(seeded_users["hand"]),
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Failed"

async def test_auditor_forbidden_from_updating_status(client, seeded_users, seeded_field_job):
    response = await client.patch(
        f"/field_jobs/{seeded_field_job.id}/status",
        json={"status": "Completed"},
        headers=auth_header(seeded_users["auditor"]),
    )
    assert response.status_code == 403

async def test_nonexistent_field_job_returns_404(client, seeded_users):
    response = await client.patch (
        "/field_jobs/999999/status",
        json={"status": "Completed"},
        headers=auth_header(seeded_users["admin"]),
    )
    assert response.status_code == 404