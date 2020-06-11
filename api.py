#!flask/bin/python

from flask import Flask, request, jsonify, Response, make_response, render_template
import json
from datetime import date
import socket

global devices
global keys

app = Flask(__name__)  # creates a flask app


# ==================================================================================
# FIREBASE IMPLEMENTATION NEEDED HERE
# ==================================================================================

# get resource from firebase
def get_resource(path):
    print("Retrieving resource from: {:}".format(path))
    return {}


# Used to write changes to JSON files out to file
def out_to_database(json_file, data):
    # write changes out to firebase
    print("Handling changes to {:}".format(json_file))

# ==================================================================================
# ==================================================================================
# ==================================================================================

# Used by /devices GET request
def access_device_file():
    global devices
    # returns the devices dictionary as a JSON file
    return jsonify(devices)


# used by POST request handler to add a new device to devices
def update_IDs():
    global devices

    # don't want to change devices directly in case another device accesses the file
    tmp_devices = devices

    # data must be in the form of a dictionary
    data = request.form

    # extract data
    device_ID = int(data["device_ID"])
    name = data["friendly_name"]
    gateway = data["controller_gateway"]

    position = len(devices) - 1  # position of new dict in devices list
    found_first = False  # condition so that the first device found with the same id will be overwritten (precaution)

    # check if device is already on the network
    for i in range(len(tmp_devices)):
        d = tmp_devices[i]  # dictionary containing JSON info of a device

        if (d["device_ID"] == device_ID) and not found_first:
            print("device_ID {:} already in use. Overwriting previous device_ID".format(device_ID))
            position = i
            found_first = True

        elif d["friendly_name"].lower() == name.lower():
            print(
                "WARNING: friendly_name in use with another device. Consider changing friendly_name and resending POST request")

    new_dict = {
        "device_ID": device_ID,
        "friendly_name": name,
        "controller_gateway": gateway
    }

    if found_first:  # if a duplicate was found
        tmp_devices[position] = new_dict

    else:
        tmp_devices.append(new_dict)

    # except:
    # return "Invalid Use Of API POST Request Handler.\nData should be in the form: {'"'device_ID'"':0,'"'friendly_name'"':'"'Example'"','"'controller_gateway'"':'"'192.168.1.9'"'}"

    out_to_database("devices.json", tmp_devices)  # write changes to file

    return Response({}, 201, mimetype="text/html")


def update_log(device_ID):
    # format of log file database:
    """
    {
    "0": [
        {
            "device_ID":0
            "current_volume": 0, 
            "date_received": "27/05/2020", 
            "total_detected": 0, 
            "total_dispenses": 0, 
            "total_ignored": 0
        }
    ]
    }
    """
    # a dictionary mapping device_IDs to a list of log files
    # need to load this in and output the update
    # the better way to do this is to find where to put it and append it to the file without reading in the whole file

    data = request.form  # get the log file

    # check the data is formatted correctly
    current_volume = int(data["current_volume"])
    total_detected = int(data["total_detected"])
    total_dispenses = int(data["total_dispenses"])
    total_ignored = int(data["total_ignored"])

    # build dictionary
    today = date.today()
    new_log = {"device_ID": int(device_ID), "date_received": str(today), "total_dispenses": total_dispenses,
               "total_detected": total_detected, "total_ignored": total_ignored, "current_volume": current_volume}

    # (log_database[str(device_ID)]).append(new_log)

    # now find device_ID in log database and write changes to file
    out_to_database("log_database.json", new_log)


# Note: POST should be used to create a resource
# PUT should be used to update a resource
# GET, DELETE, PUT, PATCH can all be called repeatedly without changing the outcome
# while POST will create duplicates
# Might have to use PATCH or POST instead of PUT for updating log file list
# A new resource is technically being created so POST might be necessary
# However PATCH could be used if the log files where addressable


# routing a call to path "/" to this method (root endpoint)
@app.route("/", methods=["GET"])
def home():
    return "<h1>Hello there</h1>"


# routing a call to path "/devices" to this method
@app.route("/devices/<api_key>", methods=["GET"])
def general_call_handler():
    # GET Handler
    if request.method == "GET":
        return access_device_file()

    else:
        return Response("<h3>ERROR: This URL is reserved for GET and HTML requests only</h3>", 501,
                        mimetype="text/html")


@app.route("/devices/<device_ID>/<api_key>", methods=["GET", "DELETE", "POST"])
def specific_call_handler(device_ID, api_key):
    global devices

    # first check if the api_key is in the database or not
    # never will be called for now, need to check with Firebase if this is a correct api key
    if False:
        return Response("<h3>Invalid API Key</h3>", 401, mimetype="text/html")

    # api_key is correct
    else:
        if request.method == "GET":
            try:
                device_ID = int(device_ID)
                # check if device_ID exists
                if device_ID in devices:
                    # if it is there, return it's information
                    # this would require pulling log files from a database
                    pass

                else:
                    # return a file not found custom error
                    return Response("<h3>Error 404: Device ID is not in use</h3>", 404, mimetype="text/html")

            except TypeError:
                return Response(
                    "<body><h3>Type Error ocuured</h3><p>This may be due to the device ID not being of numerical type.</p></body>",
                    500, mimetype="text/html")

        elif request.method == "POST":
            # dealing with log files coming from devices
            # put in a list of lists of dictionaries
            update_log(device_ID)

        elif request.method == "DELETE":
            # Attempt to delete device info with given device_ID from just the device file 
            # Look at how the devices file is configured above
            # device_ID is is nested within a dictionary, mapped to by the key "device_ID", nested within a list of similiar dictionaries
            # Therefore each ID must be checked and once one corresponding to the inputted ID is found, delete it and exit
            # Otherwise return 404
            i = 0
            while i < len(devices):
                device_info = devices[i]

                if device_info["device_ID"] == int(device_ID):
                    # delete the contents of the dictionary first
                    del device_info["device_ID"]
                    del device_info["friendly_name"]
                    del device_info["controller_gateway"]
                    break

                i += 1

            if i < len(devices) - 1:  # if an matching id was found in devices[:-1]
                devices = devices[:i] + devices[i + 1:]

            elif i == len(devices) - 1:  # if the matching id was the last device
                devices = devices[:i]

            else:  # no matching id found
                return Response("<h3>Error 404: Device ID is not in use</h3>", 404, mimetype="text/html")

            out_to_database("devices.json", devices)  # write changes to file

            return Response(204)

    return "<h1>Very cool</h1>"


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
    global devices

    # set up global devices dictionary
    # This is a dictionary of device_IDs for all devices registered on the system
    devices = get_resource("/devices")

    # get ip address of current machine
    IP = get_ip()
    print(IP)
    app.run(host=IP, port=8888, debug=True)


if __name__ == '__main__':
    main()