import io

import pytest


@pytest.mark.asyncio
async def test_create_dataset(client, auth_headers, test_user):
    workspace_id = test_user["workspace"].id
    response = await client.post(
        f"/api/datasets/?workspace_id={workspace_id}",
        json={"name": "Test Dataset", "source": "Test Source"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Dataset"


@pytest.mark.asyncio
async def test_upload_and_profile(client, auth_headers, test_user):
    workspace_id = test_user["workspace"].id
    dataset_response = await client.post(
        f"/api/datasets/?workspace_id={workspace_id}",
        json={"name": "Profile DS"},
        headers=auth_headers,
    )
    dataset_id = dataset_response.json()["id"]

    csv_content = b"id,name,value\n1,Alice,100\n2,Bob,200\n3,Charlie,\n"
    response = await client.post(
        f"/api/datasets/{dataset_id}/versions?version_tag=v1.0",
        files={"file": ("test.csv", io.BytesIO(csv_content), "text/csv")},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["record_count"] == 3
    assert data["column_count"] == 3
    assert data["profile_results"]["missing_values"]["value"] == 1
    assert len(data["content_hash"]) == 64

    versions = await client.get(f"/api/datasets/{dataset_id}/versions", headers=auth_headers)
    assert versions.status_code == 200
    assert len(versions.json()) == 1


@pytest.mark.asyncio
async def test_duplicate_version_tag_is_rejected(client, auth_headers, test_user):
    workspace_id = test_user["workspace"].id
    dataset_response = await client.post(
        f"/api/datasets/?workspace_id={workspace_id}",
        json={"name": "Version Test"},
        headers=auth_headers,
    )
    dataset_id = dataset_response.json()["id"]
    for _ in range(2):
        response = await client.post(
            f"/api/datasets/{dataset_id}/versions?version_tag=v1",
            files={"file": ("data.csv", io.BytesIO(b"id\n1\n"), "text/csv")},
            headers=auth_headers,
        )
        if _ == 0:
            assert response.status_code == 201
        else:
            assert response.status_code == 409


@pytest.mark.asyncio
async def test_workspace_isolation(client, auth_headers):
    response = await client.get("/api/datasets/?workspace_id=00000000-0000-0000-0000-000000000001", headers=auth_headers)
    assert response.status_code == 403
