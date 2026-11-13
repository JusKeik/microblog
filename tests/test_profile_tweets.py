"""Profile timelines are independent from the followed-users feed."""


def test_profile_shows_only_selected_author_newest_first(client):
    headers = {"api-key": "alice-key"}
    first = client.post(
        "/api/tweets", headers=headers, json={"tweet_data": "First"}
    ).json()["tweet_id"]
    second = client.post(
        "/api/tweets", headers=headers, json={"tweet_data": "Second"}
    ).json()["tweet_id"]
    client.post(
        "/api/tweets", headers={"api-key": "bob-key"}, json={"tweet_data": "Other"}
    )
    response = client.get("/api/users/1/tweets", headers={"api-key": "bob-key"})
    assert response.status_code == 200
    assert [tweet["id"] for tweet in response.json()["tweets"]] == [second, first]
    assert all(tweet["author"]["id"] == 1 for tweet in response.json()["tweets"])
    assert (
        client.get("/api/tweets", headers={"api-key": "bob-key"}).json()["tweets"] == []
    )
    assert len(client.get("/api/users/1/tweets", headers=headers).json()["tweets"]) == 2


def test_empty_missing_and_unauthenticated_profiles(client):
    assert client.get(
        "/api/users/1/tweets", headers={"api-key": "alice-key"}
    ).json() == {"result": True, "tweets": []}
    assert (
        client.get(
            "/api/users/999/tweets", headers={"api-key": "alice-key"}
        ).status_code
        == 404
    )
    assert client.get("/api/users/1/tweets").status_code == 401
