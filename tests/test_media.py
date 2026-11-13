from fastapi.testclient import TestClient


def test_upload_image(client: TestClient) -> None:
    response = client.post(
        "/api/medias",
        headers={"api-key": "alice-key"},
        files={"file": ("image.png", b"fake-image", "image/png")},
    )

    assert response.status_code == 200
    assert response.json()["result"] is True
    assert isinstance(response.json()["media_id"], int)


def test_upload_invalid_file_type(client: TestClient) -> None:
    response = client.post(
        "/api/medias",
        headers={"api-key": "alice-key"},
        files={"file": ("document.txt", b"text", "text/plain")},
    )

    assert response.status_code == 409
    assert response.json()["error_type"] == "conflict"