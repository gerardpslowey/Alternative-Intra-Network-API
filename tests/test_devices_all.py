# Test devices/all endpoint


def test_devices_all_get(client):
    # Request JSON device list
    r = client.get("/api/lXJdTRw8v27YDey2yBFSXg/devices/all")

    # Want a JSON response from server
    assert r.headers.get("Content-Type") == "application/json"

    # Check if request was OK
    assert r.status_code == 200


def test_devices_all_wrong_key_get(client):
    # Request JSON device list with invalid key
    r = client.get("/api/WRONG/devices/all")

    # Want a HTML response from server
    assert r.headers.get("Content-Type") == "text/html; charset=utf-8"

    # Check Unauthorised Return
    assert r.status_code == 401


def test_devices_all_post(client):
    # Attempt to post JSON to endpoint
    r = client.post("/api/lXJdTRw8v27YDey2yBFSXg/devices/all", data={})

    # Want a HTML response from server
    assert r.headers.get("Content-Type") == "text/html; charset=utf-8"

    # Check if method is not allowed
    assert r.status_code == 405
