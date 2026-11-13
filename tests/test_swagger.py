from fastapi.testclient import TestClient


def test_swagger_docs_available(client: TestClient) -> None:
    response = client.get("/docs")

    assert response.status_code == 200
    assert "swagger-ui" in response.text.lower()


def test_openapi_schema_available(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()

    assert schema["info"]["title"] == "Corporate Microblog API"
    assert "/api/tweets" in schema["paths"]
    assert "/api/users/me" in schema["paths"]
    assert "/api/medias" in schema["paths"]