import os
import sys
import time
import logging
import platform
from queue import PriorityQueue
from mainBluetooth import *
from deviceManager import *

VERSION_NUM = '1.0.0'

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
       self.queues = {
               'ble': {'send': PriorityQueue(), 'recv': PriorityQueue()},
               'socket': {'send': PriorityQueue(), 'recv': PriorityQueue()},
               }
       self.dev_manager = Device_Manager(self.queues)
       self.ble_comms = BLE_Communicator(self.dev_manager, self.queues['ble'])

    def start(self):
       logger.debug("Running comms. Press enter to exit")
       input()


logger.info(f"Starting gateway on {platform.system()}, version number: {VERSION_NUM}")
gateway = Gateway_Manager()
gateway.start()
