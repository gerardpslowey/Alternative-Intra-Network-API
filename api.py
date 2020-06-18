#!flask/bin/python

from flask import Flask, request, jsonify, Response, make_response, render_template, send_from_directory
from firebase_admin import credentials, firestore, initialize_app
from datetime import date, datetime

import socket
import time
import data_analysis 

# custom libraries
from Dispenser import Dispenser

# Get todays date
todays_date = str(date.today().strftime("%d-%m-%Y"))

# Creates a flask app
app = Flask(__name__)

# Initialize Firestore DB
cred = credentials.Certificate('ServiceAccountKey.json')
default_app = initialize_app(cred)
db = firestore.client()

# Reference to the devices collecton within the database
devices_ref = db.collection('devices')

###########################################################
####### Routing Handling ##################################
###########################################################

# Error Handling
@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


# routing a call to path "/" to this method (root endpoint)
@app.route("/", methods=["GET"])
def home():
    return "<h1>Hello there</h1>"


# routing a call to path "/devices" to this method
@app.route("/api/devices", methods=["GET", "POST", "PUT", "DELETE"])
def general_call_handler():
    # GET Handler
    if request.method == "GET":
        return access_specific_device_list()

    elif request.method == "POST":
        return add_new_device()

    elif request.method == "PUT":
        return update_usage_log_file()

    elif request.method == "DELETE":
        device_json = request.json
        device_id = device_json['deviceID']
        return remove_device_collection(devices_ref.document(device_id), 10)
    else:
        return Response("<h3>ERROR: This URL does not accept the HTTP request sent</h3>", 501,
                        mimetype="text/html")


# routing a call to path "/devices" to this method
@app.route("/api/devices/all", methods=["GET"])
def handle():
    # GET Handler
    if request.method == "GET":
        return access_all_devices_list()
    else:
        return Response("<h3>ERROR: This URL does not accept the HTTP request sent</h3>", 501,
                        mimetype="text/html")

# Browser Icon
@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Log file report
@app.route("/report", methods=["GET"])
def report_generator():
    # run graph generator
    # run requires devices (list of devices on the network) and log files
    
    # get device list
    all_devices_info = [doc.to_dict() for doc in devices_ref.stream()]
    # device_dict = jsonify(all_devices_info)

    # extract log files
    log_dict = {}

    # extract device ids only
    devices = []
    for d in all_devices_info:              # for dictionary in all_devices
        devices.append(d[u"deviceID"]) # extract ID

    for device_id in devices:
        # reference the location of the log files
        device_logs = devices_ref.document(device_id).collection(u'logs')

        # if device_id hasn't been consulted (should always be true)
        if device_id not in log_dict:
            # assuming this is the log data
            stream = device_logs.stream()

            log_dict[device_id] = [doc.to_dict() for doc in stream]

            #log_array = device_logs.document(device_id) # DocumentSnapshot

    website = data_analysis.run(devices, log_dict)

    # render website
    return render_template(website), 200

###########################################################
####### Database Functions ################################
###########################################################

def access_all_devices_list():
    try:
        all_devices = [doc.to_dict() for doc in devices_ref.stream()]
        return jsonify(all_devices), 200
    except Exception as e:
        return f"An Error Occured: {e}"


def access_specific_device_list():
    try:
        query_parameters = request.args

        # Check if ID was passed to URL query
        device_id = query_parameters.get('id')

        if device_id:
            # devices_ref is a collections refernce object
            device = devices_ref.document(device_id).get() # document snapshot

            # col = devices_ref.document(device_id).collection('logs')
            # colection within devices collection called logs, denoted by device_ids
            
            return jsonify(device.to_dict()), 200

        else:
            return "Error: No device id provided. Please specify an id."
    except Exception as e:
        return Response(f"An Error Occured: {e}")


def add_new_device():
    try:
        device_info = request.json

        # Extract the device details from the endpoint request
        deviceID = device_info['deviceID']
        deviceName = device_info['deviceName']
        gatewayController = device_info['gatewayController']
        volumeAvailable = device_info['volumeAvailable']

        # Check if the device already exists
        device_ref = devices_ref.document(deviceID)
        device = device_ref.get()

        device_ref_logs = devices_ref.document(deviceID).collection(u'logs')
        todays_log = device_ref_logs.document(todays_date)

        # Return an error message if it already is in the list
        if device.exists:
            return "ERROR: Device with deviceID already exists!\n"

        # If it doesn't, add it as a new device
        else:
            # Create instance of Dispenser class
            device = Dispenser(deviceID, deviceName, gatewayController, volumeAvailable)
            devices_ref.document(deviceID).set(device.to_dict())

            return Response("Device Successfully Added"), 200

    except Exception as e:
        return f"An Error Occurred: {e}"


def update_usage_log_file():
    current_time = str(datetime.now().strftime('%H:%M:%S'))

    # Format for a dispense record
    data = {
        u'time': current_time,
        u'volume': 1.2
        # dispensing volume hardcoded for the minute
        # consider implementing a getDispensedVolume() function (this will be in te raspberry pi code)
    }

    # Get the deviceID from the JSON body sent
    device_id = request.json['deviceID']

    # Get the location of todays log
    device_ref_logs = devices_ref.document(device_id).collection(u'logs')
    todays_log = device_ref_logs.document(todays_date)

    get_log = todays_log.get()

    try:
        if get_log.exists:
            # Atomically add a new dispense to the 'dispenses' array field.
            todays_log.update({u'dispenses': firestore.ArrayUnion([data])})
            # Delays are needed to seperate firestore operation
            time.sleep(0.1)

            # Add server timestamp to logs
            todays_log.set({
                u'Last Updated': firestore.SERVER_TIMESTAMP
            }, merge=True)
            time.sleep(0.1)

            # Increase total_dispensed value
            todays_log.update({"total_dispensed": firestore.Increment(1)})
            # Need to implement distributed counter here!!!!!!!!!!!!!!!

            return "Log file successfully updated"

        else:
            # Create the log and update
            todays_log.set({
                u'dispenses': [

                ],
                u'currentVolume': 0,
                u'total_detected': 0,
                u'total_dispensed': 0,
                u'total_ignores': 0
            })

            update_usage_log_file()

            return "Log file successfully updated"

    except Exception as e:
        return f"An Error Occurred: {e}"


def remove_device_collection(doc_ref, batch_size):
    try:

        col_ref = doc_ref.collection('logs')
        # Limit deletes at a time, prevent memory errors
        docs = col_ref.limit(batch_size).stream()
        deleted = 0

        device = doc_ref.get()

        # Check the device exists to be deleted
        if device.exists:
            # Start by deleting logs
            for doc in docs:
                print(f'Deleting doc {doc.id} => {doc.to_dict()}')
                doc.reference.delete()
                deleted = deleted + 1

            if deleted >= batch_size:
                return remove_device_collection(doc_ref, batch_size)

            # Then delete the base document
            doc_ref.delete()
            return "Device successfully deleted"

        else:
            return Response("Error: No such device!\n")

    except Exception as e:
        return f"An Error Occured: {e}"


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


def main():
    # get ip address of current machine
    IP = get_ip()

    app.run(host=IP, port=8888, debug=True)


if __name__ == '__main__':
    main()
