import os
import sys
import signal
import logging
from pybleno import *

from Characteristics import *

# instantiate Bleno and register callbacks
logger = logging.getLogger(__name__)

class BLE_Communicator:

    def __init__(self, interface, dev_manager, msg_queue, msg_handler,iface_restart_q):
        os.environ["BLENO_DEVICE_NAME"] = "wp-spectrometer-interface"
        self.bleno = Bleno()
        self.current_device = dev_manager.device
        self.dev_manager = dev_manager
        self.msg_queue = msg_queue
        self.active_client = None
        self.msg_handler = msg_handler
        self.interface = interface #currently these three aren't used
        self.is_active = True      #they're meant for symmetry in comm manager classes
        self.iface_restart_q = iface_restart_q
        
        """
          Originally the message handler was part of the BLE class
          I moved it to the gateway class so it could be shared
          between all the comms methods (BLE, Socket)
          This required the creation of this intermediate function
        """
        def send_msg_to_manager(*args):
            response = self.msg_handler(self.msg_queue, *args)
            return response

        msg_process = send_msg_to_manager

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
                laser_state = Laser_State(self.make_guid("ff03"), self.current_device, self.msg_queue, msg_process) 
                acquire_cmd = Acquire_Spectrum (self.make_guid("ff04"), self.current_device, self.msg_queue, msg_process)
                spectrum_request_cmd = Spectrum_Request(self.make_guid("ff05"), self.current_device) 
                eeprom_cmd = EEPROM_Cmd(self.make_guid("ff07"), self.current_device, self.msg_queue, msg_process)
                self.bleno.setServices([
                    BlenoPrimaryService({
                        "uuid":self.make_guid("ff00"),
                        "characteristics": [
                            IntegrationTime  (self.make_guid("ff01"), self.current_device, msg_process), 
                            Gain             (self.make_guid("ff02"), self.current_device, msg_process),
                            laser_state,
                            Scans_to_average (self.make_guid("20b4"), self.current_device), 
                            acquire_cmd,
                            spectrum_request_cmd,
                            Read_Spectrum    (self.make_guid("ff06"),acquire_cmd,spectrum_request_cmd, self.current_device, laser_state),
                            eeprom_cmd,
                            EEPROM_Data      (self.make_guid("ff08"),eeprom_cmd, self.current_device),
                            Battery_Status   (self.make_guid("ff09"), self.current_device, self.msg_queue, msg_process),
                            Detector_ROI     (self.make_guid("ff0A"), self.current_device, self.msg_queue, msg_process)
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
        self.bleno.start()

    def make_guid(self, id_code):
        PREFIX = 'D1A7'
        SUFFIX = '-AF78-4449-A34F-4DA1AFAF51BC'
        uuid = PREFIX + id_code + SUFFIX
        return uuid


    def run(self):
        pass

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
