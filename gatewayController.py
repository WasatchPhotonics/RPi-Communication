import os
import sys
import time
import logging
import platform
from queue import PriorityQueue
from mainBluetooth import *
from deviceManager import *
from socketManager import *

VERSION_NUM = '1.0.2'

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
       self.ble_comms = BLE_Communicator(self.dev_manager, self.queues['ble'], self.shared_msg_handler)
       self.sock_comms = Socket_Manager(self.dev_manager, self.queues['socket'],self.shared_msg_handler)

    def start(self):
       logger.debug("Running comms. Press enter to exit")
       input()
       
    # Used by the different communication methods BLE, Socket to send messages
    # Then return the result to that communication method
    def shared_msg_handler(self, msg_queue, request_id, request_msg, request_priority):
        data = (request_id, request_msg)
        msg_queue['send'].put_nowait((request_priority, data))
        obtained_response = False
        while not obtained_response:
            if not msg_queue['recv'].empty():
                response_id, response = msg_queue['recv'].get_nowait()
                if response_id != request_id:
                    data = (response_id, response_msg)
                    msg_queue['send'].put_nowait(request_priority, data)
                else:
                    obtained_response = True
        return response


logger.info(f"Starting gateway on {platform.system()}, version number: {VERSION_NUM}")
gateway = Gateway_Manager()
gateway.start()
