async def make_workflow(auth_client, name="Approval Test Workflow"):
    me = await auth_client.get("/me")
    user_id = me.json()["id"]
    response = await auth_client.post("/workflows/", json={
        "name": name,
        "description": "test",
        "stages": [
            {"name": "Stage 1", "order": 1, "approver_id": user_id},
            {"name": "Stage 2", "order": 2, "approver_id": user_id},
            {"name": "Stage 3", "order": 3, "approver_id": user_id},
        ]
    })
    return response.json()


async def submit_request(auth_client, workflow_id, title="Test Request"):
    response = await auth_client.post("/requests/", json={
        "workflow_id": workflow_id,
        "title": title,
        "description": "test description"
    })
    return response.json()


async def test_submit_request(auth_client):
    workflow = await make_workflow(auth_client, "Submit Test Workflow")
    response = await auth_client.post("/requests/", json={
        "workflow_id": workflow["id"],
        "title": "My Request",
        "description": "needs approval"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert data["current_stage_order"] == 1


async def test_full_approval_flow(auth_client):
    workflow = await make_workflow(auth_client, "Full Approval Workflow")
    request = await submit_request(auth_client, workflow["id"], "Full Flow Request")

    # stage 1
    r = await auth_client.post(f"/requests/{request['id']}/action", json={"action": "approved"})
    assert r.json()["current_stage_order"] == 2
    assert r.json()["status"] == "pending"

    # stage 2
    r = await auth_client.post(f"/requests/{request['id']}/action", json={"action": "approved"})
    assert r.json()["current_stage_order"] == 3
    assert r.json()["status"] == "pending"

    # stage 3 — final
    r = await auth_client.post(f"/requests/{request['id']}/action", json={"action": "approved"})
    assert r.json()["status"] == "approved"


async def test_rejection_terminates_flow(auth_client):
    workflow = await make_workflow(auth_client, "Rejection Workflow")
    request = await submit_request(auth_client, workflow["id"], "Rejection Request")

    r = await auth_client.post(f"/requests/{request['id']}/action", json={
        "action": "rejected",
        "comment": "not good enough"
    })
    assert r.json()["status"] == "rejected"


async def test_action_on_closed_request(auth_client):
    workflow = await make_workflow(auth_client, "Closed Request Workflow")
    request = await submit_request(auth_client, workflow["id"], "Closed Request")

    # reject it
    await auth_client.post(f"/requests/{request['id']}/action", json={"action": "rejected"})

    # try acting again
    r = await auth_client.post(f"/requests/{request['id']}/action", json={"action": "approved"})
    assert r.status_code == 400


async def test_invalid_action_value(auth_client):
    workflow = await make_workflow(auth_client, "Invalid Action Workflow")
    request = await submit_request(auth_client, workflow["id"], "Invalid Action Request")

    r = await auth_client.post(f"/requests/{request['id']}/action", json={"action": "maybe"})
    assert r.status_code == 400


async def test_request_not_found(auth_client):
    r = await auth_client.post("/requests/non-existent-id/action", json={"action": "approved"})
    assert r.status_code == 404


async def test_list_requests(auth_client):
    workflow = await make_workflow(auth_client, "List Requests Workflow")
    await submit_request(auth_client, workflow["id"], "List Request")
    r = await auth_client.get("/requests/")
    assert r.status_code == 200
    assert len(r.json()) >= 1