from tests.conftest import auth_header

#Happy path test - for when the correct username + password is provided
async def test_login_succeeds_with_correct_credentials(client, seeded_users):
    response = await client.post(
        "/auth/token",
        data={"username": "test_admin", "password": "password"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


#Sad path test - for when the correct username but wrong password is provided
async def test_login_fails_with_wrong_password(client, seeded_users):
    response = await client.post(
        "/auth/token",
        data={"username": "test_admin", "password": "wrong-password"},
    )
    assert response.status_code == 401

#RBAC test for the registration endpoint
async def test_register_requires_clinical_admin(client, seeded_users):
    payload = {"username": "new_user", "password": "SomePass123!", "role": "Field Hand"}

    #assert that an hand will fail
    hand_response = await client.post(
        "/auth/register", json=payload, headers=auth_header(seeded_users["hand"])
    )
    assert hand_response.status_code == 403

    #assert that an admin will succeed
    admin_response = await client.post(
        "/auth/register", json=payload, headers=auth_header(seeded_users["admin"])
    )
    assert admin_response.status_code == 201

async def test_register_rejects_case_insensitive_duplicate_username(client, seeded_users):
    payload = {"username": "TEST_ADMIN", "password": "SomePass123!", "role": "Field Hand"}
    response = await client.post("/auth/register", json=payload, headers=auth_header(seeded_users["admin"]))
    assert response.status_code == 400