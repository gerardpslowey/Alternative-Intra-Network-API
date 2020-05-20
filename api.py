import flask
from flask import request, jsonify
import json

app = flask.Flask(__name__) # creates a flask app
app.config["DEBUG"] = True  # if there is an error in the code setting this to true allows the specfic error to be displayed in browser instead of a generic bad gateway error

# read data from file "users.json"
users = []

try:
    with open("users.json") as f:
        users = json.load(f) # load users.json as a dict
        print users

except FileNotFoundError:
    pass

# Dealing with shutdown
#import signal, time, sys

#global just_pressed
#just_pressed = True # for signal handler to not call twice

def out_to_file():
    # write changes to users.json out to file
    print users
    with open("users.json", "w") as f:
        json.dump(users, f)

#def signal_handler(signal, frame):
    # handle ctrl+c event
#    global just_pressed

#    if just_pressed:
        # "CTRL + C received"
#        out_to_file()
#        just_pressed = False
#        time.sleep(1)

#    sys.exit(0)

#signal.signal(signal.SIGINT, signal_handler) # calls signal_handler on ctrl+c event

# routing a call to path "/" to this method
@app.route("/", methods=["GET"])
def home():
    return "<h1>Hello there</h1>"

# routing a call to path "/users" to this method
@app.route("/users", methods=["GET", "POST"])
def api_call():
    if request.method == "GET":
        # returns the above users dictionary as a JSON file
        return jsonify(users)

    elif request.method == "POST":
        # handles when a raspberry pi posts a log file

        #print data["ID"]
        #users["ID"] = data["ID"]
        try:
            # data must be in the form of a dictionary
            data = request.form
            print data
            user_ID_set = False
            for dict in users:
                if data["ID"] == dict["ID"]:
                    print "User already set"
                    user_ID_set = True
            if not user_ID_set:
                new_dict = {}
                new_dict["ID"] = data["ID"]
                users.append(new_dict)
                out_to_file()
        except:
            print "Invalid Use Of API POST Handler"
        
        return "<h1>Success!</h1>"

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

app.run(host=IP)




