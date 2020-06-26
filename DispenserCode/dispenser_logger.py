# Code to be run on the dispensers
# This program is used to collect dispenser statistics and send them to the central server

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  ASSUMPTIONS  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Assume the central server has a known static ip address e.g. 192.168.0.132
# This server is only visible within the private network
# The dispenser is logging info from the sensors in a file called log.JSON

from datetime import datetime

import requests
import sys
import json
import time


def runner(device_id, server_ip, log_file, device_api_key):
    # Every hour from setup the dispenser will try send data to server
    last_attempted_request = int(datetime.now().strftime('%Y%m%d%H')) # "23:00 25/06/2020" --> 2020062523

    # Should always be running on dispenser
    while True:
        current_time = int(datetime.now().strftime('%Y%m%d%H'))

        # This will near always achieve sending the requets every hour because of the way the int is constructed i.e.
        # year month day hour
        if current_time > last_attempted_request:
            # Attempt to send HTTP PUT request
            send_put_request(device_id, server_ip, log_file, device_api_key)
            # Dynamic sleep function
            sleep(log_file)


# Function to dynamically update the log files depending on usage
def sleep(log_file):
    # Maximum time to send is one hour
    time_to_wait = 3600

    with open(log_file, "r") as f:
        data = json.load(f)

        if int(data['dispenses'] <= 10):
            # Transmit every hour
            time.sleep(time_to_wait)

        elif 11 <= int(data['dispenses'] <= 100):
            # Transmit every 45 mins
            time_to_wait = 2700
            time.sleep(time_to_wait)

        elif 100 <= int(data['dispenses'] <= 250):
            # Transmit every 30 mins
            time_to_wait = 1800
            time.sleep(time_to_wait)

        else:
            # Transmit every 15 mins
            time_to_wait = 900
            time.sleep(time_to_wait)

        return


def send_put_request(device_id, server_ip, log_file, device_api_key):
    # Attempt to send a PUT request, to the server, containing the log file info
    try:
        # Open log file 
        with open(log_file, "r") as f:
            data = json.load(f)

        '''
        Format of log file:
        - {u'dispenses':[{u"time":"12:00", u"volume":1.2}], u'currentVolume': 5, u'total_detected': 3, u'total_dispensed': 2, u'total_ignores': 1}
        - JSON dict
        '''

        # Send data
        r = requests.put("http://{:}8888/api/{:}/devices?id={:}".format(server_ip, device_api_key, device_id), json=data)

        # If successful
        if r.status_code == 200:
            with open(log_file) as json_data:
                data = json.load(json_data)

                # clear the dispenses list
                # Prevents transmitting large files
                for item in data['dispenses']:
                    data.remove(item)

            # rewrite back to log file
            with open(log_file, 'w') as f:
                json.dump(data, f, indent=4)

    except requests.exceptions.ConnectionError:
        print("Unable to reach server. Will try again periodically")


if __name__ == '__main__':
    # Take required info from commandline
    device_id, server_ip, log_file, device_api_key = sys.argv[1:5]

    runner(device_id, server_ip, log_file, device_api_key)
