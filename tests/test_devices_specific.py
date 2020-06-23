# Test devices?id endpoint

def test_devices_all_ids_get(client):
    # Request JSON device list first
    devices = client.get("/api/lXJdTRw8v27YDey2yBFSXg/devices/all")

    # Want a JSON response from server
    assert devices.headers.get("Content-Type") == "application/json"

    # Check if request was OK
    assert devices.status_code == 200

    # Check data is in right format
    assert isinstance(devices.get_json(), list)

    # Extract data
    data = devices.get_json()

    device_list = []

    # Extract device IDs
    for d in data:
        # Check if dictionary
        assert isinstance(d, dict)

        # Assure that file is formatted correctly
        assert u"deviceID" in d

        # Add to device list
        device_list.append(d[u"deviceID"])

    # Go through each id and get log data
    for device_ID in device_list:
        # Endpoint of device
        endpoint = "/api/lXJdTRw8v27YDey2yBFSXg/devices?id={:}".format(device_ID)

        # Check log file
        r = client.get(endpoint)

        # Want a JSON response from server
        assert r.headers.get("Content-Type") == "application/json"

        # Check if request was OK
        assert r.status_code == 200

def test_device_id_post(client):
    # Get first device ID
    devices = client.get("/api/3FJwnCg-fHhcwQP3c59u_w/devices/all") # admin id

    # Want a JSON response from server
    #assert devices.headers.get("Content-Type") == "application/json"

    # Check if request was OK
    assert devices.status_code == 200

    # Extract data
    data = devices.get_json()

    # Extract first ID
    first = data[0][u"deviceID"]

    # Endpoint
    endpoint = "/api/3FJwnCg-fHhcwQP3c59u_w/devices?id={:}".format(first)


    def test_device_id_post_empty_data(client, endpoint):
        # Send post request
        r = client.post(endpoint, data={})

        # Check response file type
        assert r.headers.get('Content-Type') == "text/html; charset=utf-8"

        # Check if right status code
        assert r.status_code == 501

    test_device_id_post_empty_data(client, endpoint)
