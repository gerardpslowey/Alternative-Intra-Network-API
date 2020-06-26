# Test Home Page


def test_home_get(client):
    # Request home page from API
    r = client.get("/")

    # Check response file type
    assert r.headers.get('Content-Type') == "text/html; charset=utf-8"

    # Check OK
    assert r.status_code == 200


def test_home_post(client):
    # Attempt post request to create resource on home page
    r = client.post("/", data={})

    # Check response file type
    assert r.headers.get('Content-Type') == "text/html; charset=utf-8"

    # Check Method Not Allowed
    assert r.status_code == 405


def test_home_delete(client):
    # Attempt delete of none resource on home page
    r = client.delete("/", data={})

    # Check response file type
    assert r.headers.get('Content-Type') == "text/html; charset=utf-8"

    # Check Method Not Allowed
    assert r.status_code == 405
