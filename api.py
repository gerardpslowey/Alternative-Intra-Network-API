import flask
from flask import request, jsonify, Response, make_response, render_template
import json

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
devices = []

try:
    with open("devices.json") as f:
        devices = json.load(f) # load devices.json as a dict
        print devices

except:
    print "Unable to load file devices.json"

# load keys
keys = []
try:
    with open("keys.json") as f:
        keys = json.load(f)
        print keys

except:
    print "Unable to load API keys"

# Used to write chnages to JSON files out to file
def out_to_file(json_file, data):
    # write changes out to file
    with open(json_file, "w") as f:
        json.dump(data, f)


def access_device_file():
    # returns the devices dictionary as a JSON file
    return jsonify(devices)

# used by POST request handler to add a new device to devices
def update_IDs():
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

        if d["friendly_name"].lower() == name.lower():
            print "WARNING: friendly_name in use with another device. Consider changing friendly_name and resending POST request"

    new_dict = {
        "device_ID":device_ID,
        "friendly_name":name,
        "gateway":gateway
    }

    if found_first: # if a duplicate was found
        devices[position] = new_dict

    else:
        devices.append(new_dict)

    #except:
        #return "Invalid Use Of API POST Request Handler.\nData should be in the form: {'"'device_ID'"':0,'"'friendly_name'"':'"'Example'"','"'controller_gateway'"':'"'192.168.1.9'"'}"
    
    return Response({}, 201, mimetype="/devices/{:}".format(device_ID))


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


@app.route("/devices/<device_ID>/<api_key>", methods=["GET", "DELETE", "PUT"])
def specific_call_handler(device_ID, api_key):
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
            pass

        elif request.method == "DELETE":
            # attempt to delete device info with given device_ID from just the device file 
            pass

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


