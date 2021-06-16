import sys
import signal
from pybleno import *

from Characteristics import *

# instantiate Bleno and register callbacks
print("instantiating Bleno")
logger = logging.getLogger(__name__)

class BLE_Communicator:

    def __init__(self, device):
        logger = logging.getLogger(__name__)
        self.bleno = Bleno()
        self.current_device = device
        self.active_client = None

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
                laser_state = Laser_State(self.make_guid("ff03"), self.current_device) 
                acquire_cmd = Acquire_Spectrum (self.make_guid("ff04"), self.current_device)
                spectrum_request_cmd = Spectrum_Request(self.make_guid("ff05"), self.current_device) 
                eeprom_cmd = EEPROM_Cmd(self.make_guid("ff07"), self.current_device)
                self.bleno.setServices([
                    BlenoPrimaryService({
                        "uuid":self.make_guid("ff00"),
                        "characteristics": [
                            IntegrationTime  (self.make_guid("ff01"), self.current_device), 
                            Gain             (self.make_guid("ff02"), self.current_device),
                            laser_state,
                            Scans_to_average (self.make_guid("20b4"), self.current_device), 
                            acquire_cmd,
                            spectrum_request_cmd,
                            Read_Spectrum    (self.make_guid("ff06"),acquire_cmd,spectrum_request_cmd, self.current_device, laser_state),
                            eeprom_cmd,
                            EEPROM_Data      (self.make_guid("ff08"),eeprom_cmd, self.current_device),
                            Battery_Status   (self.make_guid("ff09"), self.current_device),
                            Detector_ROI     (self.make_guid("ff0A"), self.current_device)
                        ]
                    })
                ])
        def onMtuChange(mtu):
            logger.info(f"Bluetooth: Central requested new MTU of {mtu}.")

        def onAccept(clientAddress):
            logger.info(f"Bluetooth: Established new connection with {clientAddress}.")
            self.active_client = clientAddress

        def onDisconnect(clientAddress):
            logger.info(f"Bluetooth: Client {clientAddress} disconnected.")
            self.active_client = None

        # These bindings all come from pybleno's file Bleno.py
        # They are not obvious in documentation and are most easily found in the source code
        self.bleno.on("stateChange", onStateChange)
        self.bleno.on("advertisingStart", onAdvertisingStart)
        self.bleno.on("mtuChange", onMtuChange)
        self.bleno.on("accept", onAccept)
        self.bleno.on("disconnect", onDisconnect)

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
