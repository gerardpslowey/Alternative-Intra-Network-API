import flask
from flask import request, jsonify, Response, make_response, render_template
import json
from datetime import date

app = flask.Flask(__name__) # creates a flask app
app.config["DEBUG"] = True  # if there is an error in the code setting this to true allows the specfic error to be displayed in browser instead of a generic bad gateway error

# read data from file "devices.json"
"""
format: JSON

[
    {
    "device_ID":0,
    "friendly_name":"Example",
    "controller_gateway":"192.168.1.9" 
    }
    ....
]
"""

global devices
devices = []

try:
    with open("devices.json") as f:
        devices = json.load(f) # load devices.json as a dict
        print devices

except:
    print "Unable to load file devices.json"


# load keys
global keys
keys = []
try:
    with open("keys.json") as f:
        keys = json.load(f)
        print keys

except:
    print "Unable to load API keys"



# load log files at server start up
global log_database
log_database = {}

try:
    with open("log_database.json") as f:
        log_database = json.load(f) # load devices.json as a dict
        print log_database

except:
    print "Unable to load file log_database.json"


# Used to write changes to JSON files out to file
def out_to_file(json_file, data):
    # write changes out to file
    f = open(json_file, "w")
    json.dump(data, f, indent=4, encoding="utf-8", sort_keys=True)
    f.close()


def access_device_file():
    global devices
    # returns the devices dictionary as a JSON file
    return jsonify(devices)

# used by POST request handler to add a new device to devices
def update_IDs():
    global devices

    # data must be in the form of a dictionary
    data = request.form

    # extract data
    device_ID = int(data["device_ID"])
    name = data["friendly_name"]
    gateway = data["controller_gateway"]
    
    position = len(devices) - 1 # position of new dict in devices list
    found_first = False         # condition so that the first device found with the same id will be overwritten (precaution)

    # check if device is already on the network
    for i in range(len(devices)):
        d = devices[i] # dictionary containing JSON info of device

        if (d["device_ID"] == device_ID) and not found_first:
            print "device_ID {:} already in use. Overwriting previous device_ID".format(device_ID)
            position = i
            found_first = True

        elif d["friendly_name"].lower() == name.lower():
            print "WARNING: friendly_name in use with another device. Consider changing friendly_name and resending POST request"

    new_dict = {
        "device_ID":device_ID,
        "friendly_name":name,
        "controller_gateway":gateway
    }

    if found_first: # if a duplicate was found
        devices[position] = new_dict

    else:
        devices.append(new_dict)

    #except:
        #return "Invalid Use Of API POST Request Handler.\nData should be in the form: {'"'device_ID'"':0,'"'friendly_name'"':'"'Example'"','"'controller_gateway'"':'"'192.168.1.9'"'}"
    
    out_to_file("devices.json", devices) # write changes to file

    return Response({}, 201, mimetype="/devices/{:}".format(device_ID))

def update_log(device_ID):
    global log_database
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
    
    data = request.form # get the log file

    # check the data is formatted correctly
    current_volume = int(data["current_volume"])
    total_detected = int(data["total_detected"])
    total_dispenses = int(data["total_dispenses"])
    total_ignored = int(data["total_ignored"])

    # build dictionary
    today = date.today()
    new_log = {"device_ID":int(device_ID), "date_received":str(today), "total_dispenses":total_dispenses, "total_detected":total_detected, "total_ignored":total_ignored, "current_volume":current_volume}

    # now find device_ID in database and then add log file
    (log_database[str(device_ID)]).append(new_log)

    # write changes to file
    out_to_file("log_database.json", log_database)


# Note: POST should be used to create a resource
# PUT should be used to update a resource
# GET, DELETE, PUT can all be called repeatedly without changing the outcome
# while POST will create duplicates


# routing a call to path "/" to this method (root endpoint)
@app.route("/", methods=["GET"])
def home():
    return "<h1>Hello there</h1>"

# routing a call to path "/devices" to this method
@app.route("/devices", methods=["GET", "POST", "PUT", "DELETE"])
def general_call_handler():
    # GET Handler
    if request.method == "GET":
        return access_device_file()

    # POST Handler
    # handles when a new raspberry pi is added to the network
    elif request.method == "POST":
        return update_IDs()

    else:
        return Response("<h3>ERROR: This URL is reserved for GET and HTML requests only</h3>", 501, mimetype="text/html")


@app.route("/devices/<device_ID>/<api_key>", methods=["GET", "DELETE", "PUT"])
def specific_call_handler(device_ID, api_key):
    global devices
    global keys
    # first check if the api_key is correct or not
    if int(api_key) not in keys:
        return Response("<h3>Invalid API Key</h3>", 401, mimetype="text/html")

    else:
        if request.method == "GET":
            # check if device_ID exists
            if device_ID in devices:
                # if it is there, return it's information
                # this would require pulling log files from a database
                pass

            else:
                # return a file not found custom error
                return Response("<h3>Error 404: Device ID is not in use</h3>", 404, mimetype="text/html")

        elif request.method == "PUT":
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

            if i < len(devices) - 1:    # if an matching id was found in devices[:-1]
                devices = devices[:i] + devices[i+1:]

            elif i == len(devices) - 1: # if the matching id was the last device
                devices = devices[:i]

            else: # no matching id found
                return Response("<h3>Error 404: Device ID is not in use</h3>", 404, mimetype="text/html")

            out_to_file("devices.json", devices) # write changes to file

            return Response(204)

    return "<h1>Very cool</h1>"


# run on ip address of machine
# print ip address to terminal

import socket

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = "0.0.0.0"
    try:
        s.connect(("10.255.255.255", 1)) # try to connect to bogon ip to get ip of machine
        ip = s.getsockname()[0] # returns ip address of server on local network
    except:
        pass
    finally:
        s.close()
    return ip

IP = get_ip()

print IP

app.run(host=IP, port=8888)


