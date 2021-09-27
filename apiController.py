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
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from gatewayController import Gateway_Manager


load_dotenv()

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

try:
    PORT = int(os.getenv('PORT'))
    WWW_PORT = int(os.getenv('WWW_PORT'))
except:
    PORT = None
    WWW_PORT = None
DOMAIN = os.getenv('DOMAIN')
SSL_KEY = os.getenv('SSL_KEY')
SSL_CERT = os.getenv('SSL_CERT')
if PORT is None:
    PORT = 8181
if WWW_PORT is None:
    WWW_PORT = 8000

class SpecSettings(BaseModel):
    int_time: Optional[float] = None
    gain: Optional[float] = None
    laser_state: Optional[int] = None
    roi: Optional[str] = None

app = FastAPI()

wlan = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
origins = [
        f"http://192.168.1.30:8000",
        f"http://192.168.1.6",
        f"https://192.168.1.6",
        f"http://{DOMAIN}",
        f"https://{DOMAIN}",
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

@app.post("/int")
async def set_int(request: Request, spec_settings: SpecSettings):
    global msg_num
    ip = request.client.host
    msg_id = str(request.client.host) + f":{msg_num}"
    msg_num += 1
    msg_num %= 6000
    communicate_device_msg(msg_id,'SET_INT_TIME',spec_settings.int_time)
    return spec_settings

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
async def has_bat(request: Request):
    global msg_num
    ip = request.client.host
    msg_id = str(request.client.host) + f":{msg_num}"
    msg_num += 1
    msg_num %= 6000
    has_bat = communicate_device_msg(msg_id,'HAS_BATTERY',0)
    return has_bat

@app.get("/battery")
async def get_bat(request: Request):
    global msg_num
    ip = request.client.host
    msg_id = str(request.client.host) + f":{msg_num}"
    msg_num += 1
    msg_num %= 6000
    bat_per = communicate_device_msg(msg_id,'BATTERY',0)
    return bat_per

@app.get("/gain")
async def get_gain(request: Request):
    global msg_num
    ip = request.client.host
    msg_id = str(request.client.host) + f":{msg_num}"
    msg_num += 1
    msg_num %= 6000
    get_gain = communicate_device_msg(msg_id,'GET_GAIN',0)
    return get_gain

@app.post("/gain")
async def set_gain(request: Request, spec_settings: SpecSettings):
    global msg_num
    ip = request.client.host
    msg_id = str(request.client.host) + f":{msg_num}"
    msg_num += 1
    msg_num %= 6000
    communicate_device_msg(msg_id,'SET_GAIN',spec_settings.gain)
    return spec_settings

@app.get("/spectra")
async def get_spectra(request: Request):
    global msg_num
    ip = request.client.host
    port = request.url.port
    path = request.url.path
    headers = request.headers
    logger.info(f"request comes from {ip} on port {port} from path {path} with headers {headers}")
    msg_id = str(request.client.host) + f":{msg_num}"
    msg_num += 1
    msg_num %= 6000
    spectra = communicate_device_msg(msg_id,'GET_SPECTRA',0)
    return spectra

@app.get("/roi")
async def get_roi(request: Request):
    global msg_num
    ip = request.client.host
    msg_id = str(request.client.host) + f":{msg_num}"
    msg_num += 1
    msg_num %= 6000
    roi = communicate_device_msg(msg_id,'GET_ROI',0)
    return roi

@app.get("/laser_state")
async def get_laser(request: Request):
    global msg_num
    ip = request.client.host
    msg_id = str(request.client.host) + f":{msg_num}"
    msg_num += 1
    msg_num %= 6000
    laser_state = communicate_device_msg(msg_id,'GET_LASER_STATE',0)
    return laser_state

@app.post("/laser_state")
async def set_laser(request: Request, spec_settings: SpecSettings):
    global msg_num
    ip = request.client.host
    msg_id = str(request.client.host) + f":{msg_num}"
    msg_num += 1
    msg_num %= 6000
    communicate_device_msg(msg_id,'SET_LASER',str(spec_settings.laser_state))
    return spec_settings

@app.get("/watchdog_delay")
async def get_watchdog(request: Request):
    global msg_num
    ip = request.client.host
    msg_id = str(request.client.host) + f":{msg_num}"
    msg_num += 1
    msg_num %= 6000
    watchdog = communicate_device_msg(msg_id,'GET_WATCHDOG_DELAY',0)
    return watchdog

@app.get("/raman_delay")
async def get_raman_delay(request: Request):
    global msg_num
    ip = request.client.host
    msg_id = str(request.client.host) + f":{msg_num}"
    msg_num += 1
    msg_num %= 6000
    raman_delay = communicate_device_msg(msg_id,'GET_RAMAN_DELAY',0)
    return raman_delay

@app.get("/raman_mode")
async def get_raman_mode(request: Request):
    global msg_num
    ip = request.client.host
    msg_id = str(request.client.host) + f":{msg_num}"
    msg_num += 1
    msg_num %= 6000
    raman_mode = communicate_device_msg(msg_id,'GET_RAMAN_MODE',0)
    return raman_mode

if __name__ == "__main__":
    uvicorn.run(app, 
            host=["127.0.0.1",wlan], 
            port=WWW_PORT, 
            log_level="info",
            ssl_keyfile=SSL_KEY,
            ssl_certfile=SSL_CERT)
