import pytest
import io

@pytest.mark.asyncio
async def test_create_dataset(client, auth_headers, test_user):
    ws_id = test_user["workspace"].id
    response = await client.post(
        f"/api/datasets/?workspace_id={ws_id}", 
        json={"name": "Test Dataset", "source": "Test Source"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Dataset"

@pytest.mark.asyncio
async def test_upload_and_profile(client, auth_headers, test_user):
    ws_id = test_user["workspace"].id
    # Create dataset first
    ds_res = await client.post(
        f"/api/datasets/?workspace_id={ws_id}", 
        json={"name": "Profile DS"},
        headers=auth_headers
    )
    ds_id = ds_res.json()["id"]
    
    # Upload CSV
    csv_content = b"id,name,value\n1,Alice,100\n2,Bob,200\n3,Charlie,\n"
    files = {"file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
    response = await client.post(
        f"/api/datasets/{ds_id}/versions?version_tag=v1.0",
        files=files,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["record_count"] == 3
    assert data["column_count"] == 3
    assert "missing_values" in data["profile_results"]