# Code to be run on the dispensers
# This program is used to collect dispenser statistics and send them to the central server

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  ASSUMPTIONS  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Assume the central server has a known static ip address e.g. 192.168.0.132
# This server is only visible within the private network
# The dispenser is logging info from the sensors in a file called log.JSON

import requests, sys
from datetime import datetime

def runner(device_id, server_ip, log_file, device_api_key):
    # Every hour from setup the dispenser will try send data to server
    last_attempted_request = int(datetime.now().strftime('%Y%m%d%H')) # "23:00 25/06/2020" --> 2020062523

    # Should always be running on dispenser
    while True:
        current_time = int(datetime.now().strftime('%Y%m%d%H'))

        # This will near always achieve sending the requets every hour because of the way the int is constructed i.e. year month day hour
        if current_time > last_attempted_request + 1:
            # Attempt to send HTTP PUT request
            send_put_request(device_id, server_ip, log_file, device_api_key)

def send_put_request(device_id, server_ip, log_file, device_api_key):
    import json
    # Attempt to send a PUT request, to the server, containing the log file info
    try:
        # Open log file 
        with open(log_file, "r") as f:
            data = json.load(f)
            f.close()

        '''
        Format of log file:
        - {u'dispenses':[{u"time":"12:00", u"volume":1.2}], u'currentVolume': 5, u'total_detected': 3, u'total_dispensed': 2, u'total_ignores': 1}
        - JSON dict
        '''

        # Send data
        r = requests.post("http://{:}8888/api/{:}/devices?id={:}".format(server_ip, device_api_key, device_id), json=data)

        if r.status_code == 200:
            # If successful then overwrite current log file with empty file
            overwrite = open(log_file, "w")
            overwrite.close()

    except requests.exceptions.ConnectionError:
        print("Unable to reach server. Will try again periodically")

if __name__ == '__main__':
    # Take required info from commandline
    device_id, server_ip, log_file, device_api_key = sys.argv[1:5]

    runner(device_id, server_ip, log_file, device_api_key)
