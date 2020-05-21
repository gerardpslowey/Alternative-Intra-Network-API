import flask
from flask import request, jsonify
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

def out_to_file():
    # write changes to devices.json out to file
    print devices
    with open("devices.json", "w") as f:
        json.dump(devices, f)

# routing a call to path "/" to this method
@app.route("/", methods=["GET"])
def home():
    return "<h1>Hello there</h1>"

# Methods used by api call handler
def access_device_file():
    # returns the above devices dictionary as a JSON file
    return jsonify(devices)

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
        
        return "/devices/{:}".format(device_ID)

# routing a call to path "/devices" to this method
# Note: POST should be used to create a resource
# PUT should be used to update a resource
# GET, DELETE, PUT can all be called repeatedly without changing the outcome
# while POST will create duplicates

@app.route("/devices", methods=["GET", "POST", "PUT", "DELETE"])
def api_call_handler():
    # GET Handler
    if request.method == "GET":
        return access_device_file()

    # POST Handler
    # handles when a new raspberry pi is added to the network
    elif request.method == "POST":
        return update_IDs()

    # PUT Handler
    # handles when log files are updated
    elif request.method == "PUT":
        pass

    # DELETE Handler
    # handles when a device is removed from the network
    elif request.method == "DELETE":
        pass


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


