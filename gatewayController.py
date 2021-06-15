import os
import logging
from mainBluetooth import *

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)

pathname = os.getcwd()
pathname += "/pi-gateway.log"
fh = logging.FileHandler(pathname, mode='w', encoding='utf-8')
fh.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

class Gateway_Manager:
    def __init__(self):
       logger.debug("starting gateway communication methods")
       self.ble_comms = BLE_Communicator()

    def start(self):
       self.ble_comms.run()
       logger.debug("Running comms. Press enter to exit")
       input()

gateway = Gateway_Manager()
gateway.start()
