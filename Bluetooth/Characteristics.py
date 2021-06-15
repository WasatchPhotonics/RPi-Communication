import sys
import json
import array
import struct
import logging
import numpy as np

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
    def __init__(self,uuid):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': [ 'read', 'notify'], 'value': None})
        self._value = array.array('B', [0] * 0)
        self.page = None
        self.subpage = None 

    def onReadRequest(self, offset, callback):
        logger.debug("Bluetooth: batter query received")
        if device.settings.eeprom.has_battery:
            logger.debug("Bluetooth: Device has batter getting state.")
            dev_battery = device.hardware.get_battery_percentage() 
            callback(Characteristic.RESULT_SUCCESS, dev_battery.to_bytes(2,"big"))
        else:
            logger.debug("Bluetooth: Device does not have battery. Sending 100%")
            full_battery = 100
            callback(Characteristic.RESULT_SUCCESS,full_battery.to_bytes(2,"big"))

class Acquire_Spectrum(Characteristic):
    def __init__(self,uuid):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': ['write'], 'value': None})
        self._value = array.array('B',[0] * 0)
        self.current_spec = None

    def onWriteRequest(self,data,offset,withoutResponse,callback):
        logger.debug("Bluetooth: Received command to acquire spectrum")
        self.current_spec = device.take_one_averaged_reading()
        callback(Characteristic.RESULT_SUCCESS)

    def get_current_spectra(self):
        return self.current_spec

    def reset_current_spectra(self):
        self.current_spec = None

class Spectrum_Request(Characteristic):
    def __init__(self,uuid):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': [ 'write'], 'value': None})
        self._value = array.array('B',[0] * 0)
        self.pixel_offset = None

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        pixel_start_value = int.from_bytes(data, "big")
        logger.debug(f"Bluetooth: Received request to set pixel offset for spectra {pixel_start_value}")
        self.pixel_offset = pixel_start_value
        callback(Characteristic.RESULT_SUCCESS)

    def get_current_offset(self):
        return self.pixel_offset

    def reset_current_offset(self):
        self.pixel_offset = None


class EEPROM_Cmd(Characteristic):
    def __init__(self,uuid):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': [ 'write'], 'value': None})
        self._value = array.array('B', [0] * 0)
        self.page = None
        self.subpage = None

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        # data comes in as a byte array so it is easy to manipulate
        page = int(data[0])
        subpage = int(data[1])
        self.page = page
        self.subpage = subpage
        callback(Characteristic.RESULT_SUCCESS)

    def get_page(self):
        return self.page

    def get_subpage(self):
        return self.subpage

class EEPROM_Data(Characteristic):
    def __init__(self,uuid,cmd_status):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': ['read', 'notify'], 'value': None})
        self.eeprom_cmd = cmd_status
        device.settings.eeprom.generate_write_buffers()
        self._value = array.array('B', [0] * 0)
        self._updateValueCallback = None

    def onReadRequest(self, offset, callback):
        logger.debug("Bluetooth: Attempted EEPROM read")
        page = self.eeprom_cmd.get_page()
        subpage = self.eeprom_cmd.get_subpage()
        self._value = bytearray(device.settings.eeprom.write_buffers[page])[(0+16*subpage):(16+16*subpage)]
        callback(Characteristic.RESULT_SUCCESS, self._value)

    def onSubscribe(self, maxValueSize, updateValueCallback):
        logger.debug('Bluetooth: EEPROM Data subscribed to.')
        slef._updateValueCallback = updateValueCallback


class IntegrationTime(Characteristic):
    def __init__(self, uuid):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': ['read', 'write'], 'value': None})
        self._value = array.array('B', [0] * 0)
        self._updateValueCallback = None
        
    def onReadRequest(self, offset, callback):
        #logger.debug(offset, callback, self._value)
        callback(Characteristic.RESULT_SUCCESS, self._value)
        
    def onWriteRequest(self, data, offset, withoutResponse, callback):
        self._value = int.from_bytes(data,"big")
        device.change_setting("integration_time_ms", self._value)
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
    def __init__(self, uuid):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': ['read', 'write'], 'value': None})
        self._value = array.array('B', [0] * 0)
        self._updateValueCallback = None
        
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
    def __init__(self, uuid, spec_acquire, spec_cmd):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': ['read'], 'value': None})
        self._value = array.array('B', [0] * 0)
        self._updateValueCallback = None
        self.spec_acquire = spec_acquire
        self.spec_cmd = spec_cmd
        
    def onReadRequest(self, offset, callback):
        #logger.debug(self._value, self.value, callback, offset)
        logger.debug("Bluetooth: Received request to return spectrum that has been taken.")
        spec_read = self.spec_acquire.get_current_spectra()
        pixel_offset = self.spec_cmd.get_current_offset()
        reading = spec_read.spectrum
        logger.debug(f"Creating return bytes from reading. Starting at pixel {offset}")
        return_bytes = bytes()
        while len(return_bytes) < 20  and offset < len(reading):
            pixel_byte_value = reading[pixel_offset].to_bytes(2,"little")
            return_bytes += pixel_byte_value
            offset += 1
        return_bytes = pixel_offset.to_bytes(2,"big") + return_bytes
        logger.debug(f"Finished building return bytes of length {len(return_bytes)} containing up to pixel {pixel_offset} and data offset is {offset}")
        callback(Characteristic.RESULT_SUCCESS, return_bytes)

    def onSubscribe(self, maxValueSize, updateValueCallback):
        logger.debug("onSubscribe")
        self._updateValueCallback = updatevalueCallback
        
    def onUnsubscribe(self):
        logger.debug("on unsubscribe")
        self._updateValueCallback = None


class Gain(Characteristic):
    def __init__(self,uuid):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': ['read', 'write'], 'value': None})
        self._value = array.array('B', [0] * 0)
        self._updateValueCallback = None

    def onReadRequest(self, offset, callback):
        gain = device.settings.get_detector_gain()
        callback(Characteristic.RESULT_SUCCESS, gain.to_bytes(2, "big"))

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        data = bytearray(data)
        lsb = data[1]
        msb = data[0]
        gain = msb + lsb / 256.0
        logger.debug(f"Bluetooth: Updating  gain value to {gain}")
        device.hardware.set_detector_gain(gain)
        callback(Characteristic.RESULT_SUCCESS)

                  
class Laser_enable(Characteristic):
    def __init__(self, uuid):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': ['read', 'write'], 'value': None})
        self._value = array.array('B', [0] * 0)
        self._updateValueCallback = None
        
    def onReadRequest(self, offset, callback):
        logger.debug()
        callback(Characteristic.RESULT_SUCCESS, self._value)
    
    def onWriteRequest(self, data, offset, withoutResponse, callback):
        self._value = data
        if data:
            device.change_setting("laser_enable", bool(data))
            logger.debug("Laser enabled" %int(data))
        else:
            device.change_setting("laser_enable", bool(data))
            logger.debug("Laser disabled" %int(data))
        if self._updateValueCallback:
            self._updateValueCallback(self._value)
        callback(Characteristic.RESULT_SUCCESS)

    def onSubscribe(self, maxValueSize, updateValueCallback):
        logger.debug("onSubscribe")
        self._updateValueCallback = updatevalueCallback
        
    def onUnsubscribe(self):
        logger.debug("on unsubscribe")
        self._updateValueCallback = None

# when does this get run? on import?

bus = WasatchBus()
if len(bus.device_ids) == 0:
    logger.debug("No Wasatch USB spectrometers found.")
    sys.exit(0)

uid = bus.device_ids[0]
device = WasatchDevice(uid)

ok = device.connect()
device.change_setting("integration_time_ms", 10)
