import os
import sys
import time
import logging
import platform
import threading
from queue import PriorityQueue, Queue

# adds dependencies to path so end user doesnt have to
cwd = os.getcwd()
sys.path.append(''.join([cwd,'/Bluetooth']))
sys.path.append(''.join([cwd,'/Socket']))
sys.path.append(''.join([cwd,'/../Wasatch.PY']))
print(sys.path)

from mainBluetooth import *
from deviceManager import *
from socketManager import *

VERSION_NUM = '1.0.5'

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
       self.interface_restart_msg_q = Queue()
       self.dev_manager = Device_Manager(self.queues)
       self.ble_comms = BLE_Communicator('ble', 
                                        self.dev_manager, 
                                        self.queues['ble'], 
                                        self.shared_msg_handler,
                                        self.interface_restart_msg_q
                                        )
       self.wifi_sock_comms = Socket_Manager('wlan0', 
                                            self.dev_manager, 
                                            self.queues['socket'],
                                            self.shared_msg_handler,
                                            self.interface_restart_msg_q
                                            )
       self.eth_sock_comms = Socket_Manager('eth0',
                                            self.dev_manager, 
                                            self.queues['socket'], 
                                            self.shared_msg_handler,
                                            self.interface_restart_msg_q
                                            )
       self.comm_class = {
               "wlan0": Socket_Manager,
               "eth0": Socket_Manager,
               "ble": BLE_Communicator,
               }
       self.comm_instance = {
               "wlan0": self.wifi_sock_comms,
               "eth0": self.eth_sock_comms,
               "ble": self.ble_comms,
               }
       #reconn_status is used to indicate if an attempt is underway to setup the interface again
       #without this, it keeps trying to setup the interface, resulting in many unneeded instances
       interface_check_thread = threading.Thread(target=self.manager_checker)
       interface_check_thread.start()

    def start(self):
       logger.debug("Running comms.")
       input()

    def manager_checker(self):
        """Runs an infinite loop to see if the comm method has indicate the interface is down
           If it is down, try to reconnect."""
        while True:
            if not self.interface_restart_msg_q.empty():
                iface = self.interface_restart_msg_q.get_nowait()
                logger.error(f"Gateway: {iface} indicated it went down. Setting up new manager.")
                comm_class = self.comm_class[iface]
                msg_q = self.comm_instance[iface].msg_queue
                self.comm_instance[iface] = comm_class(iface,
                                                        self.dev_manager,
                                                        msg_q,
                                                        self.shared_msg_handler,
                                                        self.interface_restart_msg_q
                                                        )

    # Used by the different communication methods BLE, Socket to send messages
    # Then return the result to that communication method
    def shared_msg_handler(self, msg_queue, request_id, request_msg, request_priority):
        data = {"Id": request_id, "Message": request_msg}
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
