import sys
import json
import time
import array
import struct
import logging
import numpy as np
from copy import deepcopy

from pybleno import *

import wasatch
from wasatch.WasatchDevice import WasatchDevice
from wasatch.WasatchBus import WasatchBus
from wasatch import applog

logger = logging.getLogger(__name__)

################################################################################
#                                                                              #
#                                Characteristics                               #
#                                                                              #
################################################################################
class Battery_Status(Characteristic):
    def __init__(self, uuid, device, msg_queue, msg_func):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': [ 'read', 'notify'], 'value': None})
        self._value = array.array('B', [0] * 0)
        self.page = None
        self.subpage = None
        self.device = device
        self.guid = deepcopy(uuid)
        self.msg_num = 0
        self.msg_queue = msg_queue
        self.msg_func = msg_func

    def onReadRequest(self, offset, callback):
        logger.debug("Bluetooth: Central requested battery status.")
        msg_id = self.guid + str(self.msg_num)
        msg = {'Command': 'HAS_BATTERY', 'Value': None}
        has_battery = self.msg_func(msg_id, msg ,5)["Res_Value"]
        if has_battery:
            self.msg_num += 1
            msg_id = self.guid + str(self.msg_num)
            msg = {'Command': 'BATTERY', 'Value': None}
            dev_battery = self.msg_func(msg_id, msg , 5)["Res_Value"]
            logger.debug(f"Bluetooth: Device has battery. Returning state of {dev_battery}%.")
            self.msg_num += 1
            self.msg_num %= 8000
            dev_battery = int(dev_battery)
            callback(Characteristic.RESULT_SUCCESS, dev_battery.to_bytes(2,"big"))
        else:
            logger.debug("Bluetooth: Device does not have battery. Returning 100.%")
            full_battery = 100
            callback(Characteristic.RESULT_SUCCESS,full_battery.to_bytes(2,"big"))

class Acquire_Spectrum(Characteristic):
    def __init__(self, uuid, device, msg_queue, msg_func):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': ['write'], 'value': None})
        self._value = array.array('B',[0] * 0)
        self.current_spec = None
        self.device = device
        self.guid = deepcopy(uuid)
        self.msg_num = 0
        self.msg_queue = msg_queue
        self.msg_func = msg_func

    def onWriteRequest(self,data,offset,withoutResponse,callback):
        logger.debug("Bluetooth: Received command to acquire spectrum. Acquiring spectrum...")
        msg_id = self.guid + str(self.msg_num)
        msg = {"Command": "GET_SPECTRA", "Value": None}
        self.current_spec = self.msg_func(msg_id, msg, 5)["Res_Value"]
        self.msg_num += 1
        self.msg_num %= 8000
        callback(Characteristic.RESULT_SUCCESS)

    def get_current_spectra(self):
        return self.current_spec

    def reset_current_spectra(self):
        self.current_spec = None

class Spectrum_Request(Characteristic):
    def __init__(self, uuid, device):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': [ 'write'], 'value': None})
        self._value = array.array('B',[0] * 0)
        self.pixel_offset = None
        self.device = device

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        pixel_start_value = int.from_bytes(data, "big")
        logger.debug(f"Bluetooth: Received request to set pixel offset for spectra {pixel_start_value}.")
        self.pixel_offset = pixel_start_value
        callback(Characteristic.RESULT_SUCCESS)

    def get_current_offset(self):
        return self.pixel_offset

    def reset_current_offset(self):
        self.pixel_offset = None


class EEPROM_Cmd(Characteristic):
    def __init__(self, uuid, device, msg_queue, msg_func):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': [ 'write'], 'value': None})
        self._value = array.array('B', [0] * 0)
        self.page = None
        self.subpage = None
        self.device = device
        self.msg_queue = msg_queue
        self.write_buffers = None
        self.msg_num = 0
        self.guid = deepcopy(uuid)
        self.msg_func = msg_func

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        # data comes in as a byte array so it is easy to manipulate
        page = int(data[0])
        subpage = int(data[1])
        if page == 0 and subpage == 0:
            msg_id = self.guid + str(self.msg_num)
            msg = {'Command': 'EEPROM', 'Value': None}
            self.write_buffers = self.msg_func(msg_id, msg, 5)["Res_Value"]
            self.msg_num += 1
            self.msg_num %= 8000
        self.page = page
        self.subpage = subpage
        callback(Characteristic.RESULT_SUCCESS)

    def get_page(self):
        return self.page

    def get_subpage(self):
        return self.subpage

class EEPROM_Data(Characteristic):
    def __init__(self, uuid, cmd_status, device):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': ['read', 'notify'], 'value': None})
        self.eeprom_cmd = cmd_status
        self._value = array.array('B', [0] * 0)
        self._updateValueCallback = None
        self.device = device

    def onReadRequest(self, offset, callback):
        page = self.eeprom_cmd.get_page()
        subpage = self.eeprom_cmd.get_subpage()
        logger.debug(f"Bluetooth: Central requested EEPROM read of page {page} and subpage {subpage}")
        self._value = bytearray(self.eeprom_cmd.write_buffers[page])[(0+16*subpage):(16+16*subpage)]
        callback(Characteristic.RESULT_SUCCESS, self._value)

    def onSubscribe(self, maxValueSize, updateValueCallback):
        logger.debug('Bluetooth: EEPROM Data subscribed to.')
        slef._updateValueCallback = updateValueCallback


class IntegrationTime(Characteristic):
    def __init__(self, uuid, device, msg_func):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': ['read', 'write'], 'value': None})
        self._value = array.array('B', [0] * 0)
        self._updateValueCallback = None
        self.device = device
        self.msg_num = 0
        self.guid = deepcopy(uuid)
        self.msg_func = msg_func

        
    def onReadRequest(self, offset, callback):
        #logger.debug(offset, callback, self._value)
        msg_id = self.guid + str(self.msg_num)
        msg = {"Command": "GET_INT_TIME", "Value": None}
        self._value = self.msg_func(msg_id, msg ,5)
        self.msg_num += 1
        self.msg_num %= 8000
        logger.debug(f"Bluetooth: Got integration time of {self._value}")
        callback(Characteristic.RESULT_SUCCESS, self._value.to_bytes(2, "big"))
        
    def onWriteRequest(self, data, offset, withoutResponse, callback):
        self._value = int.from_bytes(data,"big")
        msg_id = self.guid + str(self.msg_num)
        int_value = {"Command": "SET_INT_TIME", "Value": f"{self._value}"}
        self.msg_func(msg_id, int_value, 5)
        self.msg_num += 1
        self.msg_num %= 8000
        logger.debug("Integration time changed to %d ms" % self._value)
        if self._updateValueCallback:
            self._updateValueCallback(self._value)
        callback(Characteristic.RESULT_SUCCESS)
    
    def onSubscribe(self, maxValueSize, updateValueCallback):
        logger.debug("onSubscribe")
        self._updateValueCallback = updatevalueCallback
        
    def onUnsubscribe(self):
        logger.debug("on unsubscribe")
        self._updateValueCallback = None
            
class Scans_to_average(Characteristic):
    def __init__(self, uuid, device):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': ['read', 'write'], 'value': None})
        self._value = array.array('B', [0] * 0)
        self._updateValueCallback = None
        self.device = device
        
    def onReadRequest(self, offset, callback):
        logger.debug()
        callback(Characteristic.RESULT_SUCCESS, self._value)
    
    def onWriteRequest(self, data, offset, withoutResponse, callback):
        self._value = data
        device.change_setting("scans_to_average", data)
        logger.debug("Scans average changed to %d" %int(data))
        if self._updateValueCallback:
            self._updateValueCallback(self._value)
        callback(Characteristic.RESULT_SUCCESS)

    def onSubscribe(self, maxValueSize, updateValueCallback):
        logger.debug("onSubscribe")
        self._updateValueCallback = updatevalueCallback
        
    def onUnsubscribe(self):
        logger.debug("on unsubscribe")
        self._updateValueCallback = None
                  
class Read_Spectrum(Characteristic):
    def __init__(self, uuid, spec_acquire, spec_cmd, device, laser_state):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': ['read'], 'value': None})
        self._value = array.array('B', [0] * 0)
        self._updateValueCallback = None
        self.spec_acquire = spec_acquire
        self.spec_cmd = spec_cmd
        self.device = device
        
    def onReadRequest(self, offset, callback):
        #logger.debug(self._value, self.value, callback, offset)
        logger.debug("Bluetooth: Received request to return spectrum that has been taken.")
        spec_read = self.spec_acquire.get_current_spectra()
        pixel_offset = self.spec_cmd.get_current_offset()
        reading = spec_read
        logger.debug(f"Creating return bytes from reading. Starting at pixel {pixel_offset}.")
        return_bytes = bytes()
        while len(return_bytes) < 180 and pixel_offset < len(reading):
            pixel_byte_value = reading[pixel_offset].to_bytes(2,"little")
            return_bytes += pixel_byte_value
            pixel_offset += 1
        return_bytes = pixel_offset.to_bytes(2,"big") + return_bytes
        logger.debug(f"Finished building return bytes of length {len(return_bytes)} containing up to pixel {pixel_offset}.")
        callback(Characteristic.RESULT_SUCCESS, return_bytes)

    def onSubscribe(self, maxValueSize, updateValueCallback):
        logger.debug("onSubscribe")
        self._updateValueCallback = updatevalueCallback
        
    def onUnsubscribe(self):
        logger.debug("on unsubscribe")
        self._updateValueCallback = None


class Gain(Characteristic):
    def __init__(self, uuid, device, msg_func):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': ['read', 'write'], 'value': None})
        self._value = array.array('B', [0] * 0)
        self._updateValueCallback = None
        self.device = device
        self.msg_func = msg_func
        self.guid = deepcopy(uuid)
        self.msg_num = 0

    def onReadRequest(self, offset, callback):
        msg_id = self.guid + str(msg_num)
        msg = {"Command": "GET_GAIN", "Value": None}
        gain = self.msg_func(msg_id, msg, 5)["Res_Value"]
        self.msg_num += 1
        self.msg_num %= 8000
        logger.debug("Bluetooth: Received device response for gain of {gain}")
        callback(Characteristic.RESULT_SUCCESS, gain.to_bytes(2, "big"))

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        data = bytearray(data)
        lsb = data[1]
        msb = data[0]
        gain = msb + lsb / 256.0
        msg_id = self.guid + str(self.msg_num)
        logger.debug(f"Bluetooth: Updating  gain value to {gain}")
        msg = {"Command": "SET_GAIN", "Value": f"{gain}"}
        self.msg_func(msg_id, msg, 5)
        self.msg_num += 1
        self.msg_num %= 8000
        callback(Characteristic.RESULT_SUCCESS)

                  
class Laser_State(Characteristic):
    def __init__(self, uuid, device, msg_queue, msg_func):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': ['read', 'write', 'notify'], 'value': None})
        self._value = array.array('B', [0] * 0)
        self._updateValueCallback = None
        self.raman_mode = False
        self.device = device
        self.laser_type = 0
        self.laser_enable = False
        self.laser_watchdog = False
        self.watchdog_time = 5
        self.laser_delay = 300
        self.msg_func = msg_func
        self.guid = deepcopy(uuid)
        self.msg_num = 0

    def disable_laser_error_byte(self):
        msg_id = self.guid + str(self.msg_num)
        self.device.hardware.set_laser_enable(False)
        msg = {"Command": "SET_LASER", "Value": "0"}
        self.msg_func(msg_id, msg, 0)
        self.msg_num += 1
        self.msg_num %= 8000
        logger.warn("Bluetooth: Received an incorrect byte that triggered a laser shut off.")

    def onReadRequest(self, offset, callback):
        log.debug("Bluetooth: Received laser read request.")
        msg_id = self.guid + str(self.msg_num)
        msg = {"Command": "GET_RAMAN_MODE", "Value": None}
        raman_mode = self.msg_func(msg_id, msg, 2)["Res_Value"]
        laser_type = 0
        msg = {"Command": "GET_LASER_STATE", "Value": None}
        laser_enable = self.msg_func(msg_id, msg, 2)["Res_Value"]
        msg = {"Command": "GET_WATCHDOG_DELAY", "Value": None}
        laser_watchdog = self.msg_func(msg_id, msg, 2)["Res_Value"]
        msg = {"Command": "GET_RAMAN_DELAY", "Value": None}
        laser_delay = self.msg_fun(msg_id, msg, 2)["Res_Value"] 

        return_bytes = raman_mode.to_bytes(2, "big") + laser_type.to_bytes(2, "big") + laser_enable.to_bytes(2, "big")
        return_bytes += laser_watchdog.to_bytes(2, "big") + laser_delay.to_bytes(2, "big")
        self.msg_num += 1
        self.msg_num %= 8000
        callback(Characteristic.RESULT_SUCCESS, return_bytes) 

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        logger.debug(f"Bluetooth: Received laser write request with data {data}")
        msg_id = self.guid + str(self.msg_num)
        msg_raman = int(data[0])
        msg_laser_type = int(data[1])
        msg_laser_enable = int(data[2])
        msg_laser_watch = int(data[3])
        msg_laser_delay = int.from_bytes(data[4:6], "big")
        logger.debug(f"Bluetooth: Laser message values were Raman mode {msg_raman}, Laser type {msg_laser_type}, Laser enable {msg_laser_enable}, Laser watchdog {msg_laser_watch}, and Laser delay {msg_laser_delay}.")

        if msg_raman == 0:
            self.raman_mode = False
        elif msg_raman == 1:
            self.raman_mode = True
        elif msg_raman != 255:
            self.disable_laser_error_byte()

        if msg_laser_type == 0:
            self.laser_type = 0
        elif msg_laser_type != 255:
            self.disable_laser_error_byte()

        if msg_laser_enable == 0:
            msg = {"Command": "SET_LASER", "Value": "0"}
            self.msg_func(msg_id, msg, 0)
        elif msg_laser_enable == 1:
            msg = {"Command": "SET_LASER", "Value": "1"}
            self.msg_func(msg_id, msg, 0)
        elif msg_laser_enable != 255:
            self.diable_laser_error_byte()

        if msg_laser_watch != 255:
            msg = {"Command": "SET_WATCHDOG", "Value": f"{msg_laser_watch}"}
            self.msg_func(msg_id, msg, 1)

        msg = {"Command": "SET_RAMAN_DELAY", "Value": f"{msg_laser_delay}"}
        self.msg_func(msg_id, msg, 1)
        self.msg_num += 1
        self.msg_num %= 8000
        callback(Characteristic.RESULT_SUCCESS)

    def onSubscribe(self, maxValueSize, updateValueCallback):
        logger.debug("onSubscribe")
        self._updateValueCallback = updatevalueCallback
        
    def onUnsubscribe(self):
        logger.debug("on unsubscribe")
        self._updateValueCallback = None


class Detector_ROI(Characteristic):
    def __init__(self, uuid, device, msg_queue, msg_func):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': ['read', 'write'], 'value': None})
        self._value = array.array('B', [0] * 0)
        self._updateValueCallback = None
        self.device = device
        self.guid = deepcopy(uuid)
        self.msg_num = 0
        self.msg_queue = msg_queue
        self.msg_func = msg_func

    def onReadRequest(self, offset, callback):
        logger.debug("Bluetooth: Received request for detector roi")
        msg_id = self.guid + str(self.msg_num)
        msg = {"Command": "GET_ROI", "Value": None}
        start_roi, end_roi = self.msg_func(msg_id, msg, 5)["Res_Value"]
        self.msg_num += 1
        self.msg_num %= 8000
        return_bytes = start_roi.to_bytes(2, "big") + end_roi.to_bytes(2, "big")
        logger.debug("Bluetooth: returning roi values of {start_roi} and {end_roi}")
        callback(Characteristic.RESULT_SUCCESS, return_bytes)

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        # For enlighten mobile the bytes are coming in cropped
        # This pads the bytes to the ENG-120 specific 4 in order to get the correct value
        msg_id = self.guid + str(self.msg_num)
        while len(data) < 4:
            data += bytes([0])
        start_roi = int.from_bytes(data[0:2], "big")
        end_roi = int.from_bytes(data[2:4], "big")
        logger.debug(f"Bluetooth: Received command of data {data} to set roi to {start_roi} and {end_roi}")
        msg = {"Command": "SET_ROI", "Value": f"{start_roi},{end_roi}"}
        self.msg_func(msg_id, msg, 5)
        self.msg_num += 1
        self.msg_num %= 8000
        callback(Characteristic.RESULT_SUCCESS)
