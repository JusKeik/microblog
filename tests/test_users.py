from fastapi.testclient import TestClient


def test_get_own_profile(client: TestClient) -> None:
    response = client.get(
        "/api/users/me",
        headers={"api-key": "alice-key"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["result"] is True
    assert data["user"]["name"] == "Alice"
    assert data["user"]["followers"] == []
    assert data["user"]["following"] == []


def test_follow_and_unfollow(client: TestClient) -> None:
    follow = client.post(
        "/api/users/2/follow",
        headers={"api-key": "alice-key"},
    )
    assert follow.status_code == 200
    assert follow.json() == {"result": True}

    profile = client.get(
        "/api/users/me",
        headers={"api-key": "alice-key"},
    ).json()
    assert profile["user"]["following"] == [{"id": 2, "name": "Bob"}]

    unfollow = client.delete(
        "/api/users/2/follow",
        headers={"api-key": "alice-key"},
    )
    assert unfollow.status_code == 200
    assert unfollow.json() == {"result": True}


def test_cannot_follow_self(client: TestClient) -> None:
    response = client.post(
        "/api/users/1/follow",
        headers={"api-key": "alice-key"},
    )

    assert response.status_code == 409
    assert response.json()["error_type"] == "conflict"


def test_invalid_api_key(client: TestClient) -> None:
    response = client.get(
        "/api/users/me",
        headers={"api-key": "invalid"},
    )

    assert response.status_code == 401