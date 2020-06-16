class Dispenser(object):

    def __init__(self, deviceID, deviceName, gatewayController, volumeAvailable=0):
        self.deviceID = deviceID
        self.deviceName = deviceName
        self.gatewayController = gatewayController
        self.volumeAvailable = volumeAvailable

    def to_dict(self):
        dispenser = {
            u'deviceID': self.deviceID,
            u'deviceName': self.deviceName,
            u'gatewayController': self.gatewayController
        }

        if self.deviceID:
            dispenser[u'deviceID'] = self.deviceID

        if self.deviceName:
            dispenser[u'deviceName'] = self.deviceName

        if self.gatewayController:
            dispenser[u'gatewayController'] = self.gatewayController

        if self.volumeAvailable:
            dispenser[u'volumeAvailable'] = self.volumeAvailable

        return dispenser

    def __str__(self):
        return (
            f'Dispenser(\
                deviceID={self.deviceID}, \
                deviceName={self.deviceName}, \
                gatewayController={self.gatewayController}, \
                volumeAvailable={self.volumeAvailable} \
            )'
        )
