import sys
import json
import array
import logging

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
        logging.debug("Bluetooth: batter query received")
        if device.settings.eeprom.has_battery:
            callback(Characteristic.RESULT_SUCCESS, bytes(device.hardware.get_battery_percentage()))
        else:
            callback(Characteristic.RESULT_SUCCESS,bytes(100))


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
        (f"After masking the values for page and subpage are, {page}, {subpage}")
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
        logging.debug("Attempted EEPROM read")
        page = self.eeprom_cmd.get_page()
        subpage = self.eeprom_cmd.get_subpage()
        logging.debug(f"Pages are currently {page}, {subpage}")
        logging.debug(f"EEPROM data is {device.settings.eeprom.write_buffers[page]}")
        self._value = bytearray(device.settings.eeprom.write_buffers[page])[(0+16*subpage):(16+16*subpage)]
        logging.debug(f"Length of the sending data is {len(self._value)}")
        callback(Characteristic.RESULT_SUCCESS, self._value)

    def onSubscribe(self, maxValueSize, updateValueCallback):
        logging.debug('EEPROM Data subscribed to.')
        slef._updateValueCallback = updateValueCallback


class IntegrationTime(Characteristic):
    def __init__(self, uuid):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': ['read', 'write'], 'value': None})
        self._value = array.array('B', [0] * 0)
        self._updateValueCallback = None
        
    def onReadRequest(self, offset, callback):
        #logging.debug(offset, callback, self._value)
        callback(Characteristic.RESULT_SUCCESS, self._value)
        
    def onWriteRequest(self, data, offset, withoutResponse, callback):
        self._value = data
        device.change_setting("integration_time_ms", data)
        logging.debug("Integration time changed to %d ms" % int.from_bytes(data,"big"))
        if self._updateValueCallback:
            self._updateValueCallback(self._value)
        callback(Characteristic.RESULT_SUCCESS)
    
    def onSubscribe(self, maxValueSize, updateValueCallback):
        logging.debug("onSubscribe")
        self._updateValueCallback = updatevalueCallback
        
    def onUnsubscribe(self):
        logging.debug("on unsubscribe")
        self._updateValueCallback = None
            
class Scans_to_average(Characteristic):
    def __init__(self, uuid):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': ['read', 'write'], 'value': None})
        self._value = array.array('B', [0] * 0)
        self._updateValueCallback = None
        
    def onReadRequest(self, offset, callback):
        logging.debug()
        callback(Characteristic.RESULT_SUCCESS, self._value)
    
    def onWriteRequest(self, data, offset, withoutResponse, callback):
        self._value = data
        device.change_setting("scans_to_average", data)
        logging.debug("Scans average changed to %d" %int(data))
        if self._updateValueCallback:
            self._updateValueCallback(self._value)
        callback(Characteristic.RESULT_SUCCESS)

    def onSubscribe(self, maxValueSize, updateValueCallback):
        logging.debug("onSubscribe")
        self._updateValueCallback = updatevalueCallback
        
    def onUnsubscribe(self):
        logging.debug("on unsubscribe")
        self._updateValueCallback = None
                  
class Read_Spectrum(Characteristic):
    def __init__(self, uuid):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': ['read'], 'value': None})
        self._value = array.array('B', [0] * 0)
        self._updateValueCallback = None
        
    def onReadRequest(self, offset, callback):
        #logging.debug(self._value, self.value, callback, offset)
        reading = device.acquire_data()
        logging.debug(sys.getsizeof(json.dumps(reading.spectrum)))
        self._value = bytearray(b'768')
        callback(Characteristic.RESULT_SUCCESS, array.array('B', readin))

    def onSubscribe(self, maxValueSize, updateValueCallback):
        logging.debug("onSubscribe")
        self._updateValueCallback = updatevalueCallback
        
    def onUnsubscribe(self):
        logging.debug("on unsubscribe")
        self._updateValueCallback = None
                  
class Laser_enable(Characteristic):
    def __init__(self, uuid):
        Characteristic.__init__(self, {'uuid': uuid, 'properties': ['read', 'write'], 'value': None})
        self._value = array.array('B', [0] * 0)
        self._updateValueCallback = None
        
    def onReadRequest(self, offset, callback):
        logging.debug()
        callback(Characteristic.RESULT_SUCCESS, self._value)
    
    def onWriteRequest(self, data, offset, withoutResponse, callback):
        self._value = data
        if data:
            device.change_setting("laser_enable", bool(data))
            logging.debug("Laser enabled" %int(data))
        else:
            device.change_setting("laser_enable", bool(data))
            logging.debug("Laser disabled" %int(data))
        if self._updateValueCallback:
            self._updateValueCallback(self._value)
        callback(Characteristic.RESULT_SUCCESS)

    def onSubscribe(self, maxValueSize, updateValueCallback):
        logging.debug("onSubscribe")
        self._updateValueCallback = updatevalueCallback
        
    def onUnsubscribe(self):
        logging.debug("on unsubscribe")
        self._updateValueCallback = None

# when does this get run? on import?

logger = logging.getLogger(__name__)

bus = WasatchBus()
if len(bus.device_ids) == 0:
    logging.debug("No Wasatch USB spectrometers found.")
    sys.exit(0)

uid = bus.device_ids[0]
device = WasatchDevice(uid)

ok = device.connect()
device.change_setting("integration_time_ms", 10)
