def test_openapi_json_is_reachable(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
