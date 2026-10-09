import pytest


@pytest.mark.asyncio
async def test_create_edge_and_impact(client, auth_headers, test_user):
    workspace_id = test_user["workspace"].id
    source_response = await client.post(
        f"/api/datasets/?workspace_id={workspace_id}",
        json={"name": "Source"},
        headers=auth_headers,
    )
    target_response = await client.post(
        f"/api/datasets/?workspace_id={workspace_id}",
        json={"name": "Target"},
        headers=auth_headers,
    )
    source_id = source_response.json()["id"]
    target_id = target_response.json()["id"]

    edge_response = await client.post(
        f"/api/lineage/edges?workspace_id={workspace_id}",
        json={
            "source_type": "dataset",
            "source_id": source_id,
            "target_type": "dataset",
            "target_id": target_id,
            "relationship_type": "derived_from",
        },
        headers=auth_headers,
    )
    assert edge_response.status_code == 201

    impact_response = await client.get(
        f"/api/lineage/impact?workspace_id={workspace_id}&source_type=dataset&source_id={source_id}",
        headers=auth_headers,
    )
    assert impact_response.status_code == 200
    impacts = impact_response.json()["impacts"]
    assert len(impacts) == 1
    assert impacts[0]["id"] == target_id


@pytest.mark.asyncio
async def test_lineage_graph_requires_workspace_membership(client, auth_headers):
    response = await client.get(
        "/api/lineage/graph?workspace_id=00000000-0000-0000-0000-000000000001",
        headers=auth_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_lineage_rejects_unknown_asset(client, auth_headers, test_user):
    workspace_id = test_user["workspace"].id
    response = await client.post(
        f"/api/lineage/edges?workspace_id={workspace_id}",
        json={
            "source_type": "dataset",
            "source_id": "00000000-0000-0000-0000-000000000001",
            "target_type": "dataset",
            "target_id": "00000000-0000-0000-0000-000000000002",
            "relationship_type": "derived_from",
        },
        headers=auth_headers,
    )
    assert response.status_code == 404
