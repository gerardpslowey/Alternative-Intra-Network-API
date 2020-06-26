#!flask/bin/python
from flask import Flask, request, jsonify, Response, render_template, send_from_directory
from firebase_admin import credentials, firestore, initialize_app
from datetime import date, datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Networking requirements
import socket
import time
import os

# Custom libraries
from Dispenser import Dispenser
import data_analysis


def create_app():
    # Get today's date
    todays_date = str(date.today().strftime("%d-%m-%Y"))

    # Creates a flask app
    app = Flask(__name__)

    # Initialize Firestore DB
    cred = credentials.Certificate('ServiceAccountKey.json')
    default_app = initialize_app(cred)
    db = firestore.client()

    # Reference to the devices collection within the database
    devices_ref = db.collection('devices')

    # Users authentication details
    users = {
        generate_password_hash("lXJdTRw8v27YDey2yBFSXg"): "john",
        generate_password_hash("xfvl2OiOnd0bqhyWeUuABQ"): "mary"
    }

    # Admin authentication
    admin = generate_password_hash("3FJwnCg-fHhcwQP3c59u_w")

    ###########################################################
    ####### Authentication Handling ###########################
    ###########################################################

    def verify_password(password, admin_only=False):
        # Check if admin only
        if admin_only:
            return check_password_hash(admin, password)

        # Generic user
        else:
            for key in users:
                # check every hash
                if check_password_hash(key, password):
                    return True

            if check_password_hash(admin, password):
                return True

        return False

    ###########################################################
    ####### Routing Handling ##################################
    ###########################################################

    # Error Handling

    # File Not Found
    @app.errorhandler(404)
    def page_not_found(e):
        return Response("<h1>404</h1><p>The resource could not be found.</p>", 404, mimetype="text/html")

    # Server Error
    @app.errorhandler(500)
    def server_error(e):
        return Response(
            "<h3>ERROR: The HTTP request sent caused a server error. Please consult the API documentation or contact the Network Adminstrator</h3>",
            500, mimetype="text/html")

    # HTTP endpoint not implemented
    @app.errorhandler(501)
    def not_implemented(e):
        return Response(
            "<h3>ERROR: This URL does not accept the HTTP request sent. Please consult the API documentation</h3>", 501,
            mimetype="text/html")

    # Routing a call to path "/" to this method (root endpoint)
    @app.route("/", methods=["GET"])
    def home():
        return "<h1>Hello and Welcome</h1><h3>This is the home page of our API!</h3>"

    # Example URL: http://192.168.1.9:8888/api/lXJdTRw8v27YDey2yBFSXg/devices?id=DONOTDELETE
    # routing a call to path "/devices" to this method
    @app.route("/api/<key>/devices", methods=["GET", "POST", "PUT", "DELETE"])
    def general_call_handler(key):

        # check api_key
        general_admission = verify_password(key)
        admin = verify_password(key, admin_only=True)

        if request.method == "GET":
            if general_admission:
                return access_specific_device_list()

            else:  # User only has access to get requests
                return Response("<h3>ERROR: Access to this URL content is forbidden to this user</h3>", 403, mimetype="text/html")

        # if api key is admin
        elif admin:
            if request.method == "POST":
                # add new device
                return add_new_device()

            elif request.method == "PUT":
                # add new log file
                return update_usage_log_file()

            elif request.method == "DELETE":

                # Check device id is properly formatted
                try:
                    # Extract device id
                    data = request.args
                    device_id = data.get('id')

                    # Assert it's a string
                    assert isinstance(device_id, str)

                except AssertionError:
                    return Response(
                        "<h3>ERROR: Bad Request: The request sent was malformed and did not contain possibly of the wrong type</h3>",
                        400, mimetype="text/html")

                except KeyError:
                    return Response(
                        "<h3>ERROR: Bad Request: The request sent was empty or is missing parameters</h3>",
                        400, mimetype="text/html")

                except:
                    return Response(
                        "<h3>ERROR: Bad Request: This URL does not accept the HTTP request sent. Please consult the API documentation</h3>",
                        400, mimetype="text/html")

                return remove_device_collection(devices_ref.document(device_id), 10)

        elif general_admission:  # User only has access to get requests
            return Response(
                "<h3>ERROR: This URL content is forbidden to this user</h3>",
                403, mimetype="text/html")

        # If neither conditions have been hit then return unauthorized 
        return Response(
            "<h3>ERROR: An invalid API Key has been entered: Consult Network Admin if this error persists</h3>",
            401, mimetype="text/html")

    # routing a call to path "/devices" to this method
    @app.route("/api/<key>/devices/all", methods=["GET"])
    def handle(key):

        # check api_key
        admission = verify_password(key)

        if admission and request.method == "GET":
            return access_all_devices_list()

        return Response(
            "<h3>ERROR: An invalid API Key has been entered: Consult Network Admin if this error persists</h3>",
            401, mimetype="text/html")

    # Log file report
    @app.route("/api/<key>/report", methods=["GET"])
    def report_generator(key):
        # check api_key
        if not verify_password(key):
            return Response(
                "<h3>ERROR: An invalid API Key has been entered: Consult Network Admin if this error persists</h3>",
                401, mimetype="text/html")

        # run graph generator
        # run requires devices (list of devices on the network) and log files

        # get device list
        all_devices_info = [doc.to_dict() for doc in devices_ref.stream()]

        # extract log files
        log_dict = {}

        # extract device ids only
        devices = []
        for d in all_devices_info:  # for dictionary in all_devices
            devices.append(d[u"deviceID"])  # extract ID

        for device_id in devices:
            # reference the location of the log files
            device_logs = devices_ref.document(device_id).collection(u'logs')

            # if device_id hasn't been consulted (should always be true)
            if device_id not in log_dict:
                # assuming this is the log data
                stream = device_logs.stream()

                log_dict[device_id] = [doc.to_dict() for doc in stream]

        website = data_analysis.run(devices, log_dict)

        # render website
        return render_template(website)

    # Browser Icon
    @app.route("/favicon.ico")
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',
                                   mimetype='image/vnd.microsoft.icon')

    ###########################################################
    ####### Database Functions ################################
    ###########################################################

    def access_all_devices_list():
        all_devices = [doc.to_dict() for doc in devices_ref.stream()]
        return jsonify(all_devices), 200

    def access_specific_device_list():
        query_parameters = request.args

        # Check if ID was passed to URL query
        device_id = query_parameters.get('id')

        # Document snapshot
        device = devices_ref.document(device_id).get()

        if device_id and device.exists:
            logs_d = {}

            logs_ref = devices_ref.document(device_id).collection(u'logs')
            docs = logs_ref.stream()

            # For each date add the log file
            for doc in docs:
                logs_d[doc.id] = doc.to_dict()

            # Add the device data
            this_device = [doc.to_dict() for doc in devices_ref.stream() if str(doc.id) == str(device_id)]
            logs_d[device_id] = this_device

            return logs_d

        elif device_id and not device.exists:
            return Response(
                "<h3>ERROR: Device does not exist</h3>",
                404, mimetype="text/html")

        else:
            return Response(
                "<h3>ERROR: No device id provided. Please specify an id or consult docs</h3>",
                405, mimetype="text/html")

    def add_new_device():
        device_info = {}

        try:
            # Get URL parameters
            query_parameters = request.args

            # Check if ID was passed to URL query
            device_id = query_parameters.get('id')

            assert isinstance(str(device_id), str)

            # Get data sent
            device_info = request.form

            # Extract the device details from the endpoint request and check formatting with assertions
            assert u'deviceName' in device_info
            assert isinstance(str(device_info[u'deviceName']), str)
            deviceName = device_info['deviceName']

            assert u'gatewayController' in device_info
            assert isinstance(str(device_info[u'gatewayController']), str)
            gatewayController = device_info['gatewayController']

            assert u'volumeAvailable' in device_info
            assert isinstance(float(device_info[u'volumeAvailable']), float)
            volumeAvailable = device_info['volumeAvailable']

        except AssertionError:
            return Response(
                "<h3>ERROR: Bad Request: The request sent was malformed and did not contain possibly of the wrong type</h3>",
                400, mimetype="text/html")

        except KeyError:
            return Response(
                "<h3>ERROR: Bad Request: The request sent was empty or is missing parameters</h3>",
                400, mimetype="text/html")

        except:
            return Response(
                "<h3>ERROR: Bad Request: This URL does not accept the HTTP request sent. Please consult the API documentation</h3>",
                400, mimetype="text/html")

        # Check if the device already exists
        device_ref = devices_ref.document(device_id)
        device = device_ref.get()

        # Return an error message if it already is in the list
        if device.exists:
            return Response("<h3>ERROR: Device with deviceID already exists!</h3>", 405, mimetype="text/html")

        # If it doesn't, add it as a new device
        else:
            # Create instance of Dispenser class
            device = Dispenser(device_id, deviceName, gatewayController, volumeAvailable)
            devices_ref.document(device_id).set(device.to_dict())

            # HTTP status code 201 created has no response body
            return Response(201, mimetype="text/html")

    def update_usage_log_file():
        # Get today's date and time
        todays_date = str(date.today().strftime("%d-%m-%Y"))

        # Get data from request
        data = {}
        # Default device ID
        device_id = None

        try:
            # Get URL parameters
            query_parameters = request.args

            # Check if ID was passed to URL query
            device_id = query_parameters.get('id')

            assert isinstance(str(device_id), str)

            # Get data sent in JSON request body
            data = request.json
            # print(data)

            # Assertion statements to show data is formatted correctly
            assert u'dispenses' in data
            assert isinstance(list(data[u'dispenses']), list)

            # assert that each dispense is properly formatted
            for dispense in data[u'dispenses']:
                # print(dispense)
                # time
                assert 'time' in dispense

                # dispensed volume
                assert 'volume' in dispense

                # assert only time and volume in dispense
                assert len(dispense) == 2

            assert u'currentVolume' in data
            assert isinstance(int(data[u'currentVolume']), int)

            assert u'total_detected' in data
            assert isinstance(int(data[u'total_detected']), int)

            assert u'total_dispensed' in data
            assert isinstance(int(data[u'total_dispensed']), int)

            assert u'total_ignores' in data
            assert isinstance(float(data[u'total_ignores']), float)

            # Extract data
            data = {
                u'dispenses': list(data[u'dispenses']),
                u'currentVolume': float(data[u'currentVolume']),
                u'total_detected': int(data[u'total_detected']),
                u'total_dispensed': int(data[u'total_dispensed']),
                u'total_ignores': int(data[u'total_ignores'])
            }

        except AssertionError:
            return Response(
                "<h3>ERROR: Bad Request: The request sent was malformed and did not contain possibly of the wrong type</h3>",
                400, mimetype="text/html")

        except KeyError:
            return Response("<h3>ERROR: Bad Request: The request sent was empty or is missing parameters</h3>", 400,
                            mimetype="text/html")

        except:
            return Response(
                "<h3>ERROR: Bad Request: This URL does not accept the HTTP request sent. Please consult the API documentation</h3>",
                400,
                mimetype="text/html")

        # Get the deviceID from the JSON body sent
        device = devices_ref.document(device_id).get()

        # Get the location of todays log
        device_ref_logs = devices_ref.document(device_id).collection(u'logs')
        todays_log = device_ref_logs.document(todays_date)
        get_log = todays_log.get()

        # if device id is provided and device is on system and log files already recorded
        if device_id and device.exists and get_log.exists:
            # Update the dispenses array with new data collected
            # Merge it with the old data
            todays_log.set({
                u'dispenses': data[u'dispenses']
            }, merge=True)

            # Delays are needed to separate firestore operation
            time.sleep(0.1)

            # Add server timestamp to logs
            todays_log.set({
                u'Last Updated': firestore.SERVER_TIMESTAMP
            }, merge=True)
            time.sleep(0.1)

            # Update the counter values
            todays_log.set({
                u'currentVolume': data[u'currentVolume'],
                u'total_detected': data[u'total_detected'],
                u'total_dispensed': data[u'total_dispensed'],
                u'total_ignores': data[u'total_ignores']
            }, merge=True)

            return Response("<h3>Log file successfully updated</h3>", 200, mimetype="text/html")

        elif device_id and device.exists and not get_log.exists:
            # Create the log and update
            todays_log.set({
                u'dispenses': [

                ],
                u'currentVolume': data[u'currentVolume'],
                u'total_detected': data[u'total_detected'],
                u'total_dispensed': data[u'total_dispensed'],
                u'total_ignores': data[u'total_ignores']
            })

            # Call function again now that log file has been set
            update_usage_log_file()

            return Response("<h3>Log file successfully updated</h3>", 200, mimetype="text/html")

        elif not device.exists:
            return Response("<h3>ERROR: Device does not exist</h3>", 404, mimetype="text/html")

        elif not device_id:
            return Response("<h3>ERROR: No device id provided. Please specify an id or consult docs</h3>",
                            405, mimetype="text/html")

        return Response(
            "<h3>ERROR: Bad Request: This URL does not accept the HTTP request sent. Please consult the API documentation</h3>",
            400,
            mimetype="text/html")

    def remove_device_collection(doc_ref, batch_size):
        col_ref = doc_ref.collection('logs')
        # Limit deletes at a time, prevent memory errors
        docs = col_ref.limit(batch_size).stream()
        deleted = 0

        device = doc_ref.get()

        # Check the device exists to be deleted
        if device.exists:
            # Start by deleting logs
            for doc in docs:
                # print(f'Deleting doc {doc.id} => {doc.to_dict()}')
                doc.reference.delete()
                deleted = deleted + 1

            if deleted >= batch_size:
                return remove_device_collection(doc_ref, batch_size)

            # Then delete the base document
            doc_ref.delete()
            return Response("<h3>Device successfully deleted</h3>", 200, mimetype="text/html")

        return Response("<h3>ERROR: Device does not exist</h3>", 404, mimetype="text/html")

    # run on ip address of machine
    # print ip address to terminal
    def get_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip = "0.0.0.0"
        try:
            s.connect(("10.255.255.255", 1))  # try to connect to bogon ip to get ip of machine
            ip = s.getsockname()[0]  # returns ip address of server on local network
        except:
            pass
        finally:
            s.close()
        return ip

    return app, get_ip()


if __name__ == '__main__':
    # IF API is created from this program (Could be run elsewhere for testing etc.)

    # create API
    app, IP = create_app()

    # Run API
    app.run(host=IP, port=8888, debug=True)
