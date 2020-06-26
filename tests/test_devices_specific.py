# Test devices?id endpoint


# GET testing
def test_devices_all_ids_get(client):
    # Request JSON device list 
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


# POST tests
def test_device_id_post(client):
    # Get test device ID
    test = "test"

    # Endpoint
    endpoint = "/api/3FJwnCg-fHhcwQP3c59u_w/devices?id={:}".format(test)

    def test_device_id_post_complete_data(client, endpoint, test):
        # Send post request
        r = client.post(endpoint,
                        data={"deviceName": "test", "gatewayController": "192.168.0.132", "volumeAvailable": 10})

        # Check response file type
        assert r.headers.get('Content-Type') == "text/html; charset=utf-8"

        # Check if right status code
        assert (r.status_code == 201)

    def test_device_id_post_incomplete_data(client, endpoint, test):
        # Send post request
        r = client.post(endpoint, data={"deviceName": "test", "gatewayController": "192.168.0.132"})

        # Check response file type
        assert r.headers.get('Content-Type') == "text/html; charset=utf-8"

        # Check if right status code
        assert r.status_code == 400

    def test_device_id_post_empty_data(client, endpoint, test):
        # Send post request
        r = client.post(endpoint, data={})

        # Check response file type
        assert r.headers.get('Content-Type') == "text/html; charset=utf-8"

        # Check if right status code
        assert r.status_code == 400

    def test_device_id_post_unauthorised(client, test):
        # Unauthorized access attempt
        unauth_endpoint = "/api/wrongkey/devices?id={:}".format(test)

        # Send post request
        r = client.post(unauth_endpoint,
                        data={"deviceName": "test", "gatewayController": "192.168.0.132", "volumeAvailable": 10})

        # Check response file type
        assert r.headers.get('Content-Type') == "text/html; charset=utf-8"

        # Check if right status code
        assert r.status_code == 401

    '''
    def test_device_id_post_unaethenticated(client, test):
        # Unauthenticated access attempt
        unauth_endpoint = "/api/xfvl2OiOnd0bqhyWeUuABQ/devices?id={:}".format(test)

        # Send post request
        r = client.post(endpoint, data={"deviceName":"test", "gatewayController":"192.168.0.132", "volumeAvailable":10})

        # Check response file type
        assert r.headers.get('Content-Type') == "text/html; charset=utf-8"

        # Check if right status code
        assert r.status_code == 403
    '''

    def test_device_id_already_exists(client, endpoint):
        # Send post request
        r = client.post(endpoint,
                        data={"deviceName": "test", "gatewayController": "192.168.0.132", "volumeAvailable": 10})

        # Check response file type
        assert r.headers.get('Content-Type') == "text/html; charset=utf-8"

        # Check if right status code
        assert r.status_code == 405

    def test_device_id_wrong_data_type_post(client, endpoint):
        # Send post requests

        # Test currentVolume
        r1 = client.post(endpoint, data={"deviceName": "test", "gatewayController": "192.168.0.132",
                                         "volumeAvailable": "should_be_int"})
        assert r1.status_code == 400  # Bad request

        # Test total_detected
        r2 = client.post(endpoint,
                         data={"deviceName": "test", "gatewayController": ["should_be_string"], "volumeAvailable": 10})
        assert r1.status_code == 400  # Bad request

        # Test total_dispensed
        r3 = client.post(endpoint, data={"deviceName": ["should_be_string"], "gatewayController": "192.168.0.132",
                                         "volumeAvailable": 10})
        assert r1.status_code == 400  # Bad request

        # Check responses file types
        assert r1.headers.get('Content-Type') == "text/html; charset=utf-8"
        assert r2.headers.get('Content-Type') == "text/html; charset=utf-8"
        assert r3.headers.get('Content-Type') == "text/html; charset=utf-8"

    # Call tests
    test_device_id_post_empty_data(client, endpoint, test)
    test_device_id_post_incomplete_data(client, endpoint, test)
    test_device_id_post_complete_data(client, endpoint, test)
    test_device_id_post_unauthorised(client, test)
    # test_device_id_post_unaethenticated(client, test)
    test_device_id_wrong_data_type_post(client, endpoint)


# PUT tests
def test_device_id_put(client):
    # Get test device ID
    test = "test"

    # Endpoint
    endpoint = "/api/3FJwnCg-fHhcwQP3c59u_w/devices?id={:}".format(test)

    def test_device_id_put_complete_data(client, endpoint, test):
        # Send put request
        r = client.put(endpoint, json={u'dispenses': [{u"time": "12:00", u"volume": 1.2}], u'currentVolume': 5,
                                       u'total_detected': 3, u'total_dispensed': 2, u'total_ignores': 1})

        # Check response file type
        assert r.headers.get('Content-Type') == "text/html; charset=utf-8"

        # Check if right status code
        assert r.status_code == 200

    def test_device_id_put_incomplete_data(client, endpoint, test):
        # Send put request
        r = client.put(endpoint,
                       json={u'currentVolume': 5, u'total_detected': 3, u'total_dispensed': 2, u'total_ignores': 1})

        # Check response file type
        assert r.headers.get('Content-Type') == "text/html; charset=utf-8"

        # Check if right status code
        assert r.status_code == 400

    def test_device_id_put_empty_data(client, endpoint, test):
        # Send put request
        r = client.put(endpoint, json={})

        # Check response file type
        assert r.headers.get('Content-Type') == "text/html; charset=utf-8"

        # Check if right status code
        assert r.status_code == 400

    def test_device_id_put_unauthorised(client, test):
        # Unauthorized access attempt
        unauth_endpoint = "/api/wrongkey/devices?id={:}".format(test)

        # Send put request
        r = client.put(unauth_endpoint, json={u'dispenses': [{u"time": "12:00", u"volume": 1.2}], u'currentVolume': 5,
                                              u'total_detected': 3, u'total_dispensed': 2, u'total_ignores': 1})

        # Check response file type
        assert r.headers.get('Content-Type') == "text/html; charset=utf-8"

        # Check if right status code
        assert r.status_code == 401

    '''
    def test_device_id_put_unaethenticated(client, test):
        # Unauthenticated access attempt
        unauth_endpoint = "/api/xfvl2OiOnd0bqhyWeUuABQ/devices?id={:}".format(test)

        # Send put request
        r = client.put(endpoint, json={u'dispenses':[{u"time":"It works holy fuck!!!!", u"volume":1.2}], u'currentVolume': 5, u'total_detected': 3, u'total_dispensed': 2, u'total_ignores': 1})

        # Check response file type
        assert r.headers.get('Content-Type') == "text/html; charset=utf-8"

        # Check if right status code
        assert r.status_code == 403
    '''

    def test_device_id_does_not_exist(client):
        # Send put request
        r = client.put("/api/3FJwnCg-fHhcwQP3c59u_w/devices?id=IDONTEXIST",
                       json={u'dispenses': [{u"time": "12:00", u"volume": 1.2}], u'currentVolume': 5,
                             u'total_detected': 3, u'total_dispensed': 2, u'total_ignores': 1})

        # Check response file type
        assert r.headers.get('Content-Type') == "text/html; charset=utf-8"

        # Check if right status code
        assert r.status_code == 404

    def test_device_id_wrong_data_type_put(client, endpoint):
        # Send put requests

        # Test currentVolume
        r1 = client.put(endpoint,
                        json={u'dispenses': [{u"time": "12:00", u"volume": 1.2}], u'currentVolume': "should_be_int",
                              u'total_detected': 1, u'total_dispensed': 1, u'total_ignores': 1})
        assert r1.status_code == 400  # Bad request

        # Test total_detected
        r2 = client.put(endpoint, json={u'dispenses': [{u"time": "12:00", u"volume": 1.2}], u'currentVolume': 1,
                                        u'total_detected': "should_be_int", u'total_dispensed': 1, u'total_ignores': 1})
        assert r2.status_code == 400  # Bad request

        # Test total_dispensed
        r3 = client.put(endpoint, json={u'dispenses': [{u"time": "12:00", u"volume": 1.2}], u'currentVolume': 1,
                                        u'total_detected': 1, u'total_dispensed': "should_be_int", u'total_ignores': 1})
        assert r3.status_code == 400  # Bad request

        # Test total_ignores
        r4 = client.put(endpoint, json={u'dispenses': [{u"time": "12:00", u"volume": 1.2}], u'currentVolume': 1,
                                        u'total_detected': 1, u'total_dispensed': 1, u'total_ignores': "should_be_int"})
        assert r4.status_code == 400  # Bad request

        # Test dispenses
        r5 = client.put(endpoint, json={u'dispenses': "I should be a list", u'currentVolume': 1, u'total_detected': 1,
                                        u'total_dispensed': 1, u'total_ignores': "should_be_int"})
        assert r5.status_code == 400  # Bad request

        # Check responses file types
        assert r1.headers.get('Content-Type') == "text/html; charset=utf-8"
        assert r2.headers.get('Content-Type') == "text/html; charset=utf-8"
        assert r3.headers.get('Content-Type') == "text/html; charset=utf-8"
        assert r4.headers.get('Content-Type') == "text/html; charset=utf-8"
        assert r5.headers.get('Content-Type') == "text/html; charset=utf-8"

    # Call tests
    test_device_id_put_empty_data(client, endpoint, test)
    test_device_id_put_incomplete_data(client, endpoint, test)
    test_device_id_put_complete_data(client, endpoint, test)
    test_device_id_put_unauthorised(client, test)
    # test_device_id_put_unauthenticated(client, test)
    test_device_id_wrong_data_type_put(client, endpoint)


# DELETE tests
def test_device_id_delete(client):
    # Get test device ID
    test = "test"

    # Endpoint
    endpoint = "/api/3FJwnCg-fHhcwQP3c59u_w/devices?id={:}".format(test)

    # Need to test deleting an existing id and a non existent one, authorized and otherwise
    def test_del_existent_id_unauthorized(client, test):
        unauth_endpoint = "/api/wrongkey/devices?id={:}".format(test)

        # Send delete request
        r = client.delete(unauth_endpoint)

        # Check response file type
        assert r.headers.get('Content-Type') == "text/html; charset=utf-8"

        # Check if right status code
        assert r.status_code == 401

    '''
    def test_del_existent_id_unauthenicated(client, test):
        # Unauthenticated access attempt
        unauth_endpoint = "/api/xfvl2OiOnd0bqhyWeUuABQ/devices?id={:}".format(test)

        # Send delete request
        r = client.delete(unauth_endpoint)

        # Check response file type
        assert r.headers.get('Content-Type') == "text/html; charset=utf-8"

        # Check if right status code
        assert r.status_code == 403
    '''

    def test_del_existent_id(client, endpoint, test):
        # Send delete request
        r = client.delete(endpoint)

        # Check response file type
        assert r.headers.get('Content-Type') == "text/html; charset=utf-8"

        # Check if right status code
        assert r.status_code == 200

    def test_del_non_existent_id(client, endpoint, test):
        # Send delete request
        r = client.delete("/api/3FJwnCg-fHhcwQP3c59u_w/devices?id=IDONTEXIST")

        # Check response file type
        assert r.headers.get('Content-Type') == "text/html; charset=utf-8"

        # Check if right status code
        assert r.status_code == 404

    test_del_existent_id_unauthorized(client, test)
    # test_del_existent_id_unauthenticated(client, test)
    test_del_existent_id(client, endpoint, test)
    test_del_non_existent_id(client, endpoint, test)
