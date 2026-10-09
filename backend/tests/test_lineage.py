import pytest

@pytest.mark.asyncio
async def test_create_edge_and_impact(client, auth_headers, test_user):
    ws_id = test_user["workspace"].id
    
    # Create two datasets
    ds1_res = await client.post(f"/api/datasets/?workspace_id={ws_id}", json={"name": "Source"}, headers=auth_headers)
    ds1_id = ds1_res.json()["id"]
    
    ds2_res = await client.post(f"/api/datasets/?workspace_id={ws_id}", json={"name": "Target"}, headers=auth_headers)
    ds2_id = ds2_res.json()["id"]
    
    # Create edge
    edge_res = await client.post(
        f"/api/lineage/edges?workspace_id={ws_id}",
        json={
            "source_type": "dataset",
            "source_id": ds1_id,
            "target_type": "dataset",
            "target_id": ds2_id,
            "relationship_type": "derived_from"
        },
        headers=auth_headers
    )
    assert edge_res.status_code == 200
    
    # Check impact
    impact_res = await client.get(
        f"/api/lineage/impact?workspace_id={ws_id}&source_type=dataset&source_id={ds1_id}",
        headers=auth_headers
    )
    assert impact_res.status_code == 200
    impacts = impact_res.json()["impacts"]
    assert len(impacts) == 1
    assert impacts[0]["id"] == ds2_id