import requests

url = "http://192.168.1.10:8888/api/3FJwnCg-fHhcwQP3c59u_w/devices?id=TEST1"

data = {"deviceName": "testDevice1",   "gatewayController": "192.168.1.16",  "volumeAvailable": 100}

requests.post(url, data)
