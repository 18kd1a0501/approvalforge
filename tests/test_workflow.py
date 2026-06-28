import pytest


async def make_workflow_payload(auth_client, name="Test Workflow"):
    me = await auth_client.get("/me")
    user_id = me.json()["id"]
    return {
        "name": name,
        "description": "3 stage test",
        "stages": [
            {"name": "Stage 1", "order": 1, "approver_id": user_id},
            {"name": "Stage 2", "order": 2, "approver_id": user_id},
            {"name": "Stage 3", "order": 3, "approver_id": user_id},
        ]
    }


async def test_create_workflow(auth_client):
    payload = await make_workflow_payload(auth_client, "Workflow Create Test")
    response = await auth_client.post("/workflows/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Workflow Create Test"
    assert len(data["stages"]) == 3


async def test_create_workflow_duplicate_stage_order(auth_client):
    payload = await make_workflow_payload(auth_client, "Workflow Duplicate Order")
    payload["stages"][1]["order"] = 1
    response = await auth_client.post("/workflows/", json=payload)
    assert response.status_code == 400


async def test_create_workflow_invalid_approver(auth_client):
    payload = await make_workflow_payload(auth_client, "Workflow Invalid Approver")
    payload["stages"][0]["approver_id"] = "non-existent-id"
    response = await auth_client.post("/workflows/", json=payload)
    assert response.status_code == 400


async def test_list_workflows(auth_client):
    payload = await make_workflow_payload(auth_client, "Workflow List Test")
    await auth_client.post("/workflows/", json=payload)
    response = await auth_client.get("/workflows/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


async def test_get_workflow_not_found(auth_client):
    response = await auth_client.get("/workflows/non-existent-id")
    assert response.status_code == 404