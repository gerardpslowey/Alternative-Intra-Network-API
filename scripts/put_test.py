import requests

url = "http://192.168.1.10:8888/api/3FJwnCg-fHhcwQP3c59u_w/devices?id=TESTY"

data = {
    "currentVolume": 273,
    "dispenses": [
        {
            "time": "14:51:18",
            "volume": 1.2
        },
        {
            "time": "14:51:28",
            "volume": 1.2
        },
        {
            "time": "14:52:00",
            "volume": 1.2
        },
        {
            "time": "14:52:08",
            "volume": 1.2
        }
    ],
    "total_detected": 5,
    "total_dispensed": 4,
    "total_ignores": 1
}


requests.put(url, data)
