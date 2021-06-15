import sys
import signal
from pybleno import *

from Characteristics import *

# instantiate Bleno and register callbacks
print("instantiating Bleno")
logger = logging.getLogger(__name__)

class BLE_Communicator:

    def __init__(self):
        logger = logging.getLogger(__name__)
        self.bleno = Bleno()

        def onStateChange(state):
            logger.info('on -> stateChange: ' + state);
            if(state == "poweredOn"):
                logger.info("Bluetooth: broadcasting gateway available for connections")
                self.bleno.startAdvertising("wp-Spectrometer", ["dfdc"])
            else:
                logger.info(f"Bluetooth: connection initiated {state}")
                self.bleno.stopAdvertising()


        def onAdvertisingStart(error):
            logger.info('on -> advertisingStart: ' + ('error ' + error if error else 'success'));
            if error:
                print(error)
            else:
                logger.info("Configuring bleno services")
                eeprom_cmd = EEPROM_Cmd(self.make_guid("ff07"))
                self.bleno.setServices([
                    BlenoPrimaryService({
                        "uuid":self.make_guid("ff00"),
                        "characteristics": [
                            IntegrationTime (self.make_guid("ff01")), 
                            Scans_to_average(self.make_guid("20b4")), 
                            Laser_enable    (self.make_guid("7610")), 
                            Read_Spectrum   (self.make_guid("ff06")),
                            eeprom_cmd,
                            EEPROM_Data     (self.make_guid("ff08"),eeprom_cmd),
                            Battery_Status  (self.make_guid("ff09"))
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
        logger.info("Closing Bleno")
        self.bleno.stopAdvertising()
        self.bleno.disconnect()
        logger.info("terminated")

        


if __name__ == "__main__":
    BLE = BLE_Communicator()
    BLE.run()
    print("Press <enter> to exit...")
    if sys.version_info > (3, 0):
        input()
    else:
        raw_input()
