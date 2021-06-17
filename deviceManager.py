import sys
import logging
import threading

from wasatch.WasatchDevice import WasatchDevice
from wasatch.WasatchBus import WasatchBus

logger = logging.getLogger(__name__)

class Device_Manager:
    def __init__(self, msg_queues):
        self.msg_queues = msg_queues
        bus = WasatchBus()
        if len(bus.device_ids) == 0:
            logger.warn("No spectrometer detected. Exiting.")
            sys.exit(0)
        uid = bus.device_ids[0]
        self.device = WasatchDevice(uid)
        ok = self.device.connect()
        self.device.change_setting("integration_time_ms", 10)

        thread = threading.Thread(target=self.device_worker, daemon=True)
        thread.start()

    def device_worker(self):
        while True:
            for comm_method in self.msg_queues.keys():
                if not self.msg_queues[comm_method]['send'].empty():
                    msg_id, msg = self.msg_queues[comm_method]['send'].get_nowait()
                    logger.debug(f'Device Manager: Received request from {comm_method} of {msg}')
                    self.process_msg(msg_id, msg, comm_method)

    def process_msg(self, msg_id, msg, comm_method):

        msg_response_funcs = {
                'EEPROM': self.get_eeprom,
                }
        msg_response = msg_response_funcs[msg]()
        self.msg_queues[comm_method]['recv'].put((msg_id, msg_response))


    def get_eeprom(self):
        self.device.settings.eeprom.generate_write_buffers()
        eeprom = self.device.settings.eeprom.write_buffers
        return eeprom

