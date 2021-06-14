import sys
import signal
from pybleno import *

from Characteristics import *

# instantiate Bleno and register callbacks
print("instantiating Bleno")

class BLE_Communicator:

    def __init__(self):
        self.bleno = Bleno()

        def onStateChange(state):
            print('on -> stateChange: ' + state);
            if(state == "poweredOn"):
                self.bleno.startAdvertising("wp-Spectrometer", ["dfdc"])
            else:
                self.bleno.stopAdvertising()


        def onAdvertisingStart(error):
            print('on -> advertisingStart: ' + ('error ' + error if error else 'success'));
            if error:
                print(error)
            else:
                print("Configuring bleno services")
                self.bleno.setServices([
                    BlenoPrimaryService({
                        "uuid":self.make_guid("ff00"),
                        "characteristics": [
                            IntegrationTime (self.make_guid("ff01")), 
                            Scans_to_average(self.make_guid("20b4")), 
                            Laser_enable    (self.make_guid("7610")), 
                            Read_Spectrum   (self.make_guid("ff06"))
                        ]
                    })
                ])

        self.bleno.on("stateChange", onStateChange)
        self.bleno.on("advertisingStart", onAdvertisingStart)

    def make_guid(self, id_code):
        PREFIX = 'D1A7'
        SUFFIX = '-AF78-4449-A34F-4DA1AFAF51BC'
        uuid = PREFIX + id_code + SUFFIX
        return uuid


    def run(self):
        self.bleno.start()

    def disconnect(self):
        print("Closing Bleno")
        self.bleno.stopAdvertising()
        self.bleno.disconnect()
        print("terminated")

        


if __name__ == "__main__":
    BLE = BLE_Communicator()
    BLE.run()
    print("Press <enter> to exit...")
    if sys.version_info > (3, 0):
        input()
    else:
        raw_input()
