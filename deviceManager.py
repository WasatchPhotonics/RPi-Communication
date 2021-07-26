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
            logger.warn("Device Manager: No spectrometer detected. Exiting.")
            sys.exit(0)
        uid = bus.device_ids[0]
        self.device = WasatchDevice(uid)
        ok = self.device.connect()
        self.device.change_setting("integration_time_ms", 10)
        self.msg_response_funcs = {
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

        thread = threading.Thread(target=self.device_worker)
        thread.start()

    # According to Wasatch Device process_commands is usually continuously updated from continuous poll
    # This does not happen in many of these asynchronous commands 
    # So this function ensures they arent stuck in the queue
    def update_settings(self):
        self.device.process_commands()

    def is_valid_command(self, command):
        command = command.replace('\n','')
        command = command.upper()
        return self.msg_response_funcs.get(command,False)

    def device_worker(self):
        while True:
            for comm_method in self.msg_queues.keys():
                if not self.msg_queues[comm_method]['send'].empty():
                    priority, data  = self.msg_queues[comm_method]['send'].get_nowait()
                    msg_id = data["Id"]
                    msg = data["Message"]
                    logger.debug(f"Device Manager: Received request from {comm_method} of {msg}")
                    self.process_msg(msg_id, msg, comm_method)

    def process_msg(self, msg_id, msg, comm_method):
        msg_cmd = msg['Command'].upper()
        process_func = None
        process_func = self.msg_response_funcs.get(msg_cmd,None)
        if process_func is not None:
            msg_response = process_func(msg['Value'])
            if msg_response["Error"] is not None:
                logger.error(f"Device Manager: Encountered error of {msg_response[1]} while handling msg {msg} from msg id {msg_id}")
            self.msg_queues[comm_method]['recv'].put((msg_id, msg_response))
        else:
            logger.error(f"Device Manager: Received invalid request of {msg} from msg id {msg_id}")
            self.msg_queues[comm_method]['recv'].put((msg_id,'INVALID_OPTION'))
        
    def get_eeprom(self, not_used):
        self.device.settings.eeprom.generate_write_buffers()
        eeprom = self.device.settings.eeprom.write_buffers
        return {"Res_Value": eeprom, "Error": None}

    def has_battery(self, not_used):
        return {"Res_Value": self.device.settings.eeprom.has_battery, "Error": None}

    def battery(self, not_used):
        return {"Res_Value": self.device.hardware.get_battery_percentage(), "Error": None}

    def get_gain(self, not_used):
        return {"Res_Value": self.device.settings.get_detector_gain(), "Error": None}

    def set_gain(self, gain_value):
        try:
            gain_value = float(gain_value)
            self.device.hardware.set_detector_gain(gain_value)
            self.update_settings()
            return {"Res_Value": True, "Error": None}
        except TypeError:
            logger.error(f"Device Manager: Invalid type while in set_gain for gain_value of {type(gain_value)}")
            return {"Res_Value": False, "Error": f"Invalid type for gain of {type(gain_value)}"}

    def set_int_time(self, int_value):
        try:
            int_value = float(int_value)
            self.device.change_setting("integration_time_ms",int_value)
            self.update_settings()
            return {"Res_Value": True, "Error": None}
        except TypeError:
            logger.error(f"Device Manager: Invalid type while in set_int_time for int_value of {type(int_value)}")
            return {"Res_Value": False, "Error": f"Invalid type for integration time of {type(int_value)}"}

    def get_int_time(self, not_used):
        return {"Res_Value": self.device.hardware.get_integration_time_ms(), "Error": None}

    def get_spectra(self, not_used):
        self.device.acquire_data()
        return {"Res_Value": self.device.acquire_data().spectrum, "Error": None}

    def get_roi(self, not_used):
        start_roi = self.device.settings.eeprom.roi_horizontal_start
        end_roi = self.device.settings.eeprom.roi_horizontal_end
        return {"Res_Value": (start_roi, end_roi), "Error": None}

    def set_roi(self, roi_values):
        try:
            start_roi, end_roi = roi_values.split(',')
            self.device.hardware.set_vertical_binning([int(start_roi), int(end_roi)])
            return {"Res_Value": True, "Error": None}
        except TypeError:
            logger.error(f"Device Manager: Invalid type while in set_roi for roi values of {type(roi_values)}")
            return {"Res_Value": False, "Error": f"Received invalid roi type, start type of {type(roi_values)}"}
        except ValueError:
            logger.error(f"Device Manager: Invalid value for roi values {roi_values}")
            return {"Res_Value": False, "Error": f"Received invalid roi values of {roi_values}"}
        except AttributeError:
            logger.error(f"Device Manager: Attribute error in set_roi for value of {roi_values}")
            return {"Res_Value": False, "Error": f"Received invalid roi values of {roi_values}"}

    def set_laser(self, enabled):
        if enabled == '1':
            self.device.hardware.set_laser_enable(True)
            return {"Res_Value": True, "Error": None}
        else:
            self.device.hardware.set_laser_enable(False)
            return {"Res_Value": False, "Error": None}

    def set_laser_watchdog(self,timeout):
        try:
            self.device.hardware.set_laser_watchdog_sec(int(timeout))
            return {"Res_Value": True, "Error": None}
        except TypeError:
            logger.error(f"Device Manager: Invalid type while in set_laser_watchdog for timeout of {type(timeout)}")
            return {"Res_Value": False, "Error": f"Invalid type for watchdog timeout of {type(timeout)}"}

    def set_raman_delay(self,delay_time):
        try:
            self.device.hardware.set_raman_delay_ms(int(delay_time))
            return {"Res_Value": True, "Error": None}
        except TypeError:
            logger.error(f"Device Manager: Invalid type while in set_raman_delay for delay_time of {type(delay_time)}")
            return {"Res_Value": False, "Error": f'Invalid tpye for raman delay time of {type(delay_time)}'}

    def get_laser_state(self, not_used):
        return {"Res_Value": self.device.hardware.get_laser_enable(), "Error": None}

    def get_watch_delay(self, not_used):
        return {"Res_Value": self.device.hardware.get_laser_watchdog_sec(), "Error": None}

    def get_raman_delay(self, not_used):
        return {"Res_Value": self.device.hardware.get_raman_delay_ms(), "Error": None}

    def get_raman_mode(self, not_used):
        return {"Res_Value": self.device.hardware.get_raman_mode_enable_NOT_USED(), "Error": None}
