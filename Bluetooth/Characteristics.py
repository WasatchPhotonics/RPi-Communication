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
    def __init__(self, uuid, device):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': [ 'read', 'notify'], 'value': None})
        self._value = array.array('B', [0] * 0)
        self.page = None
        self.subpage = None
        self.device = device

    def onReadRequest(self, offset, callback):
        logger.debug("Bluetooth: Central requested battery status.")
        if self.device.settings.eeprom.has_battery:
            dev_battery = self.device.hardware.get_battery_percentage() 
            logger.debug(f"Bluetooth: Device has battery. Returning state of {dev_battery}%.")
            callback(Characteristic.RESULT_SUCCESS, dev_battery.to_bytes(2,"big"))
        else:
            logger.debug("Bluetooth: Device does not have battery. Returning 100.%")
            full_battery = 100
            callback(Characteristic.RESULT_SUCCESS,full_battery.to_bytes(2,"big"))

class Acquire_Spectrum(Characteristic):
    def __init__(self, uuid, device):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': ['write'], 'value': None})
        self._value = array.array('B',[0] * 0)
        self.current_spec = None
        self.device = device

    def onWriteRequest(self,data,offset,withoutResponse,callback):
        logger.debug("Bluetooth: Received command to acquire spectrum. Acquiring spectrum...")
        self.current_spec = self.device.acquire_data()
        self.current_spec = self.device.acquire_data()
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
    def __init__(self, uuid, device, msg_queue):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': [ 'write'], 'value': None})
        self._value = array.array('B', [0] * 0)
        self.page = None
        self.subpage = None
        self.device = device
        self.msg_queue = msg_queue
        self.write_buffers = None
        self.msg_num = 0
        self.guid = deepcopy(uuid)

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        # data comes in as a byte array so it is easy to manipulate
        page = int(data[0])
        subpage = int(data[1])
        if page == 0 and subpage == 0:
            msg_id = self.guid + str(self.msg_num)
            #self.device.settings.eeprom.read_eeprom()
            #self.device.settings.eeprom.generate_write_buffers()
            self.msg_queue['send'].put_nowait((msg_id, 'EEPROM'))
            obtained_response = False
            while not obtained_response:
                if not self.msg_queue['recv'].empty():
                    response_id, response = self.msg_queue['recv'].get_nowait()
                    logger.debug(f"Bluetooth: Got device response of id {response_id}")
                    if response_id != msg_id:
                        self.msg_queue['send'].put_nowait((response_id,response))
                    else:
                        self.write_buffers = response
                        obtained_response = True
            self.msg_num += 1 % 8000
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
    def __init__(self, uuid, device):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': ['read', 'write'], 'value': None})
        self._value = array.array('B', [0] * 0)
        self._updateValueCallback = None
        self.device = device
        
    def onReadRequest(self, offset, callback):
        #logger.debug(offset, callback, self._value)
        callback(Characteristic.RESULT_SUCCESS, self._value)
        
    def onWriteRequest(self, data, offset, withoutResponse, callback):
        self._value = int.from_bytes(data,"big")
        self.device.change_setting("integration_time_ms", self._value)
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
        reading = spec_read.spectrum
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
    def __init__(self, uuid, device):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': ['read', 'write'], 'value': None})
        self._value = array.array('B', [0] * 0)
        self._updateValueCallback = None
        self.device = device

    def onReadRequest(self, offset, callback):
        gain = self.device.settings.get_detector_gain()
        callback(Characteristic.RESULT_SUCCESS, gain.to_bytes(2, "big"))

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        data = bytearray(data)
        lsb = data[1]
        msb = data[0]
        gain = msb + lsb / 256.0
        logger.debug(f"Bluetooth: Updating  gain value to {gain}")
        self.device.hardware.set_detector_gain(gain)
        callback(Characteristic.RESULT_SUCCESS)

                  
class Laser_State(Characteristic):
    def __init__(self, uuid, device):
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

    def disable_laser_error_byte(self):
        self.device.hardware.set_laser_enable(False)
        logger.warn("Bluetooth: Received an incorrect byte that triggered a laser shut off.")

    def onReadRequest(self, offset, callback):
        log.debug("Bluetooth: Received laser read request.")
        raman_mode = self.device.hardware.get_raman_mode_enable_NOT_USED()
        laser_type = 0
        laser_enable = self.device.hardware.get_laser_enable()
        laser_watchdog = self.device.hardware.get_laser_watchdog_sec()
        laser_delay = self.device.hardware.get_raman_delay_ms()

        return_bytes = raman_mode.to_bytes(2, "big") + laser_type.to_bytes(2, "big") + laser_enable.to_bytes(2, "big")
        return_bytes += laser_watchdog.to_bytes(2, "big") + laser_delay.to_bytes(2, "big")
        callback(Characteristic.RESULT_SUCCESS, return_bytes) 

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        logger.debug(f"Bluetooth: Received laser write request with data {data}")
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
            self.device.hardware.set_laser_enable(False)
        elif msg_laser_enable == 1:
            self.device.hardware.set_laser_enable(True)
        elif msg_laser_enable != 255:
            self.diable_laser_error_byte()

        if msg_laser_watch != 255:
            self.device.hardware.set_laser_watchdog_sec(msg_laser_watch) 

        self.device.hardware.set_raman_delay_ms(msg_laser_delay)
        callback(Characteristic.RESULT_SUCCESS)

    def onSubscribe(self, maxValueSize, updateValueCallback):
        logger.debug("onSubscribe")
        self._updateValueCallback = updatevalueCallback
        
    def onUnsubscribe(self):
        logger.debug("on unsubscribe")
        self._updateValueCallback = None


class Detector_ROI(Characteristic):
    def __init__(self, uuid, device):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': ['read', 'write'], 'value': None})
        self._value = array.array('B', [0] * 0)
        self._updateValueCallback = None
        self.device = device

    def onReadRequest(self, offset, callback):
        logger.debug("Bluetooth: Received request for detector roi")
        start_roi = self.device.settings.eeprom.roi_horizontal_start
        end_roi = self.device.settings.eeprom.roi_horizontal_end
        return_bytes = start_roi.to_bytes(2, "big") + end_roi.to_bytes(2, "big")
        callback(Characteristic.RESULT_SUCCESS, return_bytes)

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        # For enlighten mobile the bytes are coming in cropped
        # This pads the bytes to the ENG-120 specific 4 in order to get the correct value
        while len(data) < 4:
            data += bytes([0])
        start_roi = int.from_bytes(data[0:2], "big")
        end_roi = int.from_bytes(data[2:4], "big")
        logger.debug(f"Bluetooth: Received command of data {data} to set roi to {start_roi} and {end_roi}")
        self.device.hardware.set_vertical_binning([start_roi, end_roi])
        callback(Characteristic.RESULT_SUCCESS)
