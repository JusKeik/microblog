"""Regression checks for the requirements and deployment integration."""

import pytest


def test_unknown_api_returns_json_error(client):
    response = client.get("/api/does-not-exist")
    assert response.status_code == 404
    assert response.json() == {
        "result": False,
        "error_type": "http_error",
        "error_message": "Not found",
    }


def test_static_assets_and_spa_routes(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert "<html" in client.get("/login").text
    response = client.get("/js/app.ee2cdef2.js")
    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]
    assert client.get("/js/missing.js").status_code == 404


@pytest.mark.parametrize("payload", [{}, {"tweet_data": ""}, {"tweet_data": "x" * 501}])
def test_invalid_tweet_has_documented_error(client, payload):
    response = client.post(
        "/api/tweets", headers={"api-key": "alice-key"}, json=payload
    )
    assert response.status_code == 422
    assert response.json()["result"] is False
    assert response.json()["error_type"] == "validation_error"


def test_media_attachment_ownership_and_deletion(client):
    image = client.post(
        "/api/medias",
        headers={"api-key": "alice-key"},
        files={"file": ("pic.png", b"\x89PNG\r\n\x1a\ndata", "image/png")},
    )
    media_id = image.json()["media_id"]
    payload = {"tweet_data": "With image", "tweet_media_ids": [media_id]}
    forbidden = client.post("/api/tweets", headers={"api-key": "bob-key"}, json=payload)
    assert forbidden.status_code == 404
    created = client.post("/api/tweets", headers={"api-key": "alice-key"}, json=payload)
    tweet_id = created.json()["tweet_id"]
    reused = client.post("/api/tweets", headers={"api-key": "alice-key"}, json=payload)
    assert reused.status_code == 404
    client.post("/api/users/1/follow", headers={"api-key": "bob-key"})
    feed = client.get("/api/tweets", headers={"api-key": "bob-key"}).json()["tweets"]
    assert feed[0]["id"] == tweet_id
    assert feed[0]["attachments"][0].startswith("/static/media/")
    assert client.get(feed[0]["attachments"][0]).content == b"\x89PNG\r\n\x1a\ndata"
    client.post(f"/api/tweets/{tweet_id}/likes", headers={"api-key": "bob-key"})
    assert (
        client.delete(
            f"/api/tweets/{tweet_id}", headers={"api-key": "alice-key"}
        ).status_code
        == 200
    )
    assert (
        client.get("/api/tweets", headers={"api-key": "bob-key"}).json()["tweets"] == []
    )


@pytest.mark.parametrize(
    "content,mime",
    [
        (b"bad-image", "image/png"),
        (b"RIFF1234WAVEdata", "image/webp"),
        (b"\x89PNG\r\n\x1a\ndata", "image/jpeg"),
        (b"", "image/png"),
        (b"x" * (5 * 1024 * 1024 + 1), "image/png"),
    ],
)
def test_reject_invalid_media(client, content, mime):
    response = client.post(
        "/api/medias",
        headers={"api-key": "alice-key"},
        files={"file": ("file", content, mime)},
    )
    assert response.status_code == 409
    assert response.json()["result"] is False


def test_feed_excludes_unfollowed_users(client):
    client.post(
        "/api/tweets", headers={"api-key": "bob-key"}, json={"tweet_data": "Hidden"}
    )
    assert (
        client.get("/api/tweets", headers={"api-key": "alice-key"}).json()["tweets"]
        == []
    )


def test_all_api_responses_have_error_schema(client):
    schema = client.get("/openapi.json").json()
    for path, methods in schema["paths"].items():
        if not path.startswith("/api/"):
            continue
        for operation in methods.values():
            for status in ("401", "403", "404", "409", "422", "500"):
                model = operation["responses"][status]["content"]["application/json"][
                    "schema"
                ]
                assert model["$ref"].endswith("/ErrorResponse")
