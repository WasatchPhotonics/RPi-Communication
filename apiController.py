import os
import sys
import json
import time
import socket
import uvicorn
import logging
import platform
import threading
import netifaces as ni
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from gatewayController import Gateway_Manager

PORT = 8181

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

app = FastAPI()

wlan = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
origins = [
        f"http://{wlan}:3000"
    ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])

gateway = None
s = None
msg_num = 0

def communicate_device_msg(msg_id, command, value):
    global s
    cmd_msg = {'ID':msg_id,'Command':command,'Value':value,'Error':None}
    cmd_msg = json.dumps(cmd_msg)
    try:
        s.send(bytes(cmd_msg,encoding='utf-8'))
        msg = []
        response = s.recv(4096)
        total_msg_received = len(response[2:])
        msg_len = int.from_bytes(response[:2], "big")
        msg.append(response[2:])
        while total_msg_received < msg_len:
            response = s.recv(4096)
            if response is None or response.decode('utf-8') == '':
                return
            msg.append(response)
            total_msg_received += len(response)
        complete_msg = b''.join(msg)
        complete_msg = json.loads(complete_msg)
        complete_msg['ID'] = msg_id
        return complete_msg                
    except Exception as e:
        return f"Error: Failed to send command due to {e}"

@app.on_event("startup")
async def start_upevent():
    global s
    global gateway
    gateway = Gateway_Manager()
    time.sleep(2)
    addr = '127.0.0.1'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((addr,PORT))
    
@app.get("/int")
async def get_int(request: Request):
    global msg_num
    ip = request.client.host
    msg_id = str(request.client.host) + f":{msg_num}"
    msg_num += 1
    msg_num %= 6000
    int_time = communicate_device_msg(msg_id,'GET_INT_TIME',0)
    return int_time

@app.get("/eeprom")
async def get_eeprom(request: Request):
    global msg_num
    ip = request.client.host
    msg_id = str(request.client.host) + f":{msg_num}"
    msg_num += 1
    msg_num %= 6000
    eeprom = communicate_device_msg(msg_id,'EEPROM',0)
    return eeprom

@app.get("/has_battery")
async def get_eeprom(request: Request):
    global msg_num
    ip = request.client.host
    msg_id = str(request.client.host) + f":{msg_num}"
    msg_num += 1
    msg_num %= 6000
    has_bat = communicate_device_msg(msg_id,'HAS_BATTERY',0)
    return has_bat

@app.get("/battery")
async def get_eeprom(request: Request):
    global msg_num
    ip = request.client.host
    msg_id = str(request.client.host) + f":{msg_num}"
    msg_num += 1
    msg_num %= 6000
    bat_per = communicate_device_msg(msg_id,'BATTERY',0)
    return bat_per

@app.get("/gain")
async def get_eeprom(request: Request):
    global msg_num
    ip = request.client.host
    msg_id = str(request.client.host) + f":{msg_num}"
    msg_num += 1
    msg_num %= 6000
    get_gain = communicate_device_msg(msg_id,'GET_GAIN',0)
    return get_gain

@app.get("/spectra")
async def get_eeprom(request: Request):
    global msg_num
    ip = request.client.host
    msg_id = str(request.client.host) + f":{msg_num}"
    msg_num += 1
    msg_num %= 6000
    spectra = communicate_device_msg(msg_id,'GET_SPECTRA',0)
    return spectra

@app.get("/roi")
async def get_eeprom(request: Request):
    global msg_num
    ip = request.client.host
    msg_id = str(request.client.host) + f":{msg_num}"
    msg_num += 1
    msg_num %= 6000
    roi = communicate_device_msg(msg_id,'GET_ROI',0)
    return roi

@app.get("/laser_state")
async def get_eeprom(request: Request):
    global msg_num
    ip = request.client.host
    msg_id = str(request.client.host) + f":{msg_num}"
    msg_num += 1
    msg_num %= 6000
    laser_state = communicate_device_msg(msg_id,'GET_LASER_STATE',0)
    return laser_state

@app.get("/watchdog_delay")
async def get_eeprom(request: Request):
    global msg_num
    ip = request.client.host
    msg_id = str(request.client.host) + f":{msg_num}"
    msg_num += 1
    msg_num %= 6000
    watchdog = communicate_device_msg(msg_id,'GET_WATCHDOG_DELAY',0)
    return watchdog

@app.get("/raman_delay")
async def get_eeprom(request: Request):
    global msg_num
    ip = request.client.host
    msg_id = str(request.client.host) + f":{msg_num}"
    msg_num += 1
    msg_num %= 6000
    raman_delay = communicate_device_msg(msg_id,'GET_RAMAN_DELAY',0)
    return raman_delay

@app.get("/raman_mode")
async def get_eeprom(request: Request):
    global msg_num
    ip = request.client.host
    msg_id = str(request.client.host) + f":{msg_num}"
    msg_num += 1
    msg_num %= 6000
    raman_mode = communicate_device_msg(msg_id,'GET_RAMAN_MODE',0)
    return raman_mode

if __name__ == "__main__":
    uvicorn.run(app, host=["127.0.0.1",wlan], port=8000, log_level="info")
