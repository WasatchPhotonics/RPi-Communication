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
                    priority, data  = self.msg_queues[comm_method]['send'].get_nowait()
                    msg_id, msg = data
                    logger.debug(f'Device Manager: Received request from {comm_method} of {msg}')
                    self.process_msg(msg_id, msg, comm_method)

    def process_msg(self, msg_id, msg, comm_method):

        msg_response_funcs = {
                'EEPROM': self.get_eeprom,
                'HAS_BATTERY': self.has_battery,
                'BATTERY': self.battery,
                'GET_GAIN': self.get_gain,
                'SET_GAIN': self.set_gain,
                'SET_INT_TIME': self.set_int_time,
                'GET_INT_TIME': self.get_int_time,
                'GET_SPECTRA': self.get_spectra,
                'GET_ROI': self.get_roi,
                'SET_ROI': self.set_roi,
                'SET_LASER': self.set_laser,
                'SET_WATCHDOG': self.set_laser_watchdog,
                'SET_RAMAN_DELAY': self.set_raman_delay,
                'GET_LASER_STATE': self.get_laser_state,
                'GET_WATCHDOG_DELAY': self.get_watch_delay,
                'GET_RAMAN_DELAY': self.get_raman_delay,
                'GET_RAMAN_MODE': self.get_raman_mode,
                }
        values = msg.split(":")
        set_value = None
        if len(values) == 2:
            msg = values[0]
            set_value = values[1]
        process_func = msg_response_funcs.get(msg,None)
        if process_func is not None:
            msg_response = process_func(set_value)
            self.msg_queues[comm_method]['recv'].put((msg_id, msg_response))
        else:
            logger.error(f"Device Manager: Received invalid request of {msg}")


    def get_eeprom(self, not_used):
        self.device.settings.eeprom.generate_write_buffers()
        eeprom = self.device.settings.eeprom.write_buffers
        return eeprom

    def has_battery(self, not_used):
        return self.device.settings.eeprom.has_battery

    def battery(self, not_used):
        return self.device.hardware.get_battery_percentage()

    def get_gain(self, not_used):
        return self.device.settings.get_detector_gain()

    def set_gain(self, gain_value):
        gain_value = float(gain_value)
        self.device.hardware.set_detector_gain(gain_value)
        return True

    def set_int_time(self, int_value):
        int_value = float(int_value)
        self.device.change_setting("integration_time_ms",int_value)
        return True

    def get_int_time(self, not_used):
        return self.device.hardware.get_integration_time_ms()

    def get_spectra(self, not_used):
        self.device.acquire_data()
        return self.device.acquire_data()

    def get_roi(self, not_used):
        start_roi = self.device.settings.eeprom.roi_horizontal_start
        end_roi = self.device.settings.eeprom.roi_horizontal_end
        return (start_roi, end_roi)

    def set_roi(self, roi_values):
        start_roi, end_roi = roi_values.split(',')
        self.device.hardware.set_vertical_binning([int(start_roi), int(end_roi)])
        return True

    def set_laser(self, enabled):
        if enabled == '1':
            self.device.hardware.set_laser_enable(True)
        else:
            self.device.hardware.set_laser_enable(False)

    def set_laser_watchdog(self,timeout):
        self.device.hardware.set_laser_watchdog_sec(int(timeout))

    def set_raman_delay(self,delay_time):
        self.device.hardware.set_raman_delay_ms(int(delay_time))

    def get_laser_state(self):
        return self.device.hardware.get_laser_enable()

    def get_watch_delay(self):
        return self.device.hardware.get_laser_watchdog_sec()

    def get_raman_delay(self):
        return self.device.hardware.get_raman_delay_ms()

    def get_raman_mode(self):
        return self.device.hardware.get_raman_mode_enable_NOT_USED()
