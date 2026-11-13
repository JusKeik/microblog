from fastapi.testclient import TestClient


def test_create_tweet(client: TestClient) -> None:
    response = client.post(
        "/api/tweets",
        headers={"api-key": "alice-key"},
        json={"tweet_data": "Первый твит", "tweet_media_ids": []},
    )

    assert response.status_code == 201
    assert response.json() == {"result": True, "tweet_id": 1}


def test_create_tweet_requires_api_key(client: TestClient) -> None:
    response = client.post(
        "/api/tweets",
        json={"tweet_data": "Текст"},
    )

    assert response.status_code == 422


def test_delete_someone_elses_tweet(client: TestClient) -> None:
    created = client.post(
        "/api/tweets",
        headers={"api-key": "alice-key"},
        json={"tweet_data": "Твит Alice"},
    )
    tweet_id = created.json()["tweet_id"]

    response = client.delete(
        f"/api/tweets/{tweet_id}",
        headers={"api-key": "bob-key"},
    )

    assert response.status_code == 403
    assert response.json()["result"] is False


def test_like_and_unlike_tweet(client: TestClient) -> None:
    created = client.post(
        "/api/tweets",
        headers={"api-key": "alice-key"},
        json={"tweet_data": "Твит для лайка"},
    )
    tweet_id = created.json()["tweet_id"]

    like = client.post(
        f"/api/tweets/{tweet_id}/likes",
        headers={"api-key": "bob-key"},
    )
    assert like.status_code == 200
    assert like.json() == {"result": True}

    duplicate = client.post(
        f"/api/tweets/{tweet_id}/likes",
        headers={"api-key": "bob-key"},
    )
    assert duplicate.status_code == 403

    unlike = client.delete(
        f"/api/tweets/{tweet_id}/likes",
        headers={"api-key": "bob-key"},
    )
    assert unlike.status_code == 200
    assert unlike.json() == {"result": True}


def test_feed_sorted_by_popularity(client: TestClient) -> None:
    client.post(
        "/api/users/2/follow",
        headers={"api-key": "alice-key"},
    )
    client.post(
        "/api/users/3/follow",
        headers={"api-key": "alice-key"},
    )

    first = client.post(
        "/api/tweets",
        headers={"api-key": "bob-key"},
        json={"tweet_data": "Обычный твит"},
    ).json()["tweet_id"]

    second = client.post(
        "/api/tweets",
        headers={"api-key": "carol-key"},
        json={"tweet_data": "Популярный твит"},
    ).json()["tweet_id"]

    client.post(
        f"/api/tweets/{second}/likes",
        headers={"api-key": "alice-key"},
    )

    response = client.get(
        "/api/tweets",
        headers={"api-key": "alice-key"},
    )

    assert response.status_code == 200
    tweets = response.json()["tweets"]
    assert [tweet["id"] for tweet in tweets] == [second, first]