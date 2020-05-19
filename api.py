import flask
from flask import request, jsonify
import json

app = flask.Flask(__name__) # creates a flask app
app.config["DEBUG"] = True  # if there is an error in the code setting this to true allows the specfic error to be displayed in browser instead of a generic bad gateway error

# read data from file "users.json"
users = {}

try:
    with open("users.json") as f:
        users = json.load(f) # load users.json as a dict

except FileNotFoundError:
    pass

# Dealing with shutdown
import signal, time, sys

def out_to_file():
    # write changes to users.json out to file
    with open("users.json", "w") as f:
        json.dump(users, f)

def signal_handler(signal, frame):
    # handle ctrl+c event
    print "CTRL + C received"
    out_to_file()
    time.sleep(1)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler) # calls signal_handler on ctrl+c event

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
        data = request.form
        print data["ID"]
        users["ID"] = data["ID"]

app.run()



