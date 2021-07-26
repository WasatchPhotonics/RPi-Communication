import json
import time
import socket
import logging
import threading
import netifaces as ni
from netifaces import AF_INET

logger = logging.getLogger(__name__)

class Socket_Manager:
    def __init__(self, interface, device_manager, msg_queues, msg_handler):
        self.port = 8181
        self.server_addr = None

        self.format = 'utf-8'
        self.interface = interface
        self.dev_manager = device_manager
        self.msg_queue = msg_queues
        self.msg_len = None
        self.msg_num = 0
        self.conn_attempt = 0
        self.server_socket = None
        self.msg_handler = msg_handler
        server_thread = threading.Thread(target=self.socket_thread)
        server_thread.start()

    def socket_thread(self):
        # keep trying to create a socket if there is no address
        # For example if there is no ethernet cord
        while self.server_addr is None:
            try:
                # This is the way to access interface ip4 addr using ifaces
                # See https://stackoverflow.com/questions/6243276/how-to-get-the-physical-interface-ip-address-from-an-interface
                self.server_addr = ni.ifaddresses(self.interface)[AF_INET][0]['addr']
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.bind((self.server_addr, self.port))
            except Exception as e:
                if self.conn_attempt < 5:
                    logger.error(f"While trying to get {self.interface} address encountered error {e}. Waiting 5 seconds before trying to get interface address again.")
                elif self.conn_attempt == 5:
                    logger.error(f"While trying to get {self.interface} address encountered error {e}. Already searched 5 times. Continuing search but suppressing log statements.")
                self.conn_attempt += 1
                time.sleep(5)
                continue
        self.conn_attempt = 0
        self.server_socket.listen()
        logger.info(f"Socket: started server interface {self.interface} listening on {self.server_addr} on port {self.port}")
        while True:
            client_socket, addr = self.server_socket.accept()
            client = threading.Thread(target=self.client_thread, args=(client_socket,addr))
            client.start()

    def client_thread(self, client_conn, client_addr):
        logger.info(f"Socket: Received new client connection from address {client_addr}")
        while True:
            recv_msg = client_conn.recv(1024)
            if not recv_msg:
                client_conn.close()
                logger.info(f"Socket: Received blank command from {client_addr}. Closing connection")
                break
            else:
                """
                layout of command is Command_Name:Args
                Command_Name corresponds to dict values in device manager
                This is needed for args that do vs do not have args
                e.g. EEPROM vs SET_INT_TIME:13
                """
                recv_msg = json.loads(recv_msg)
                recv_msg = dict(recv_msg)
                command = recv_msg['Command'].upper()
                command_values = recv_msg['Value']
                command_setting = ''
                logger.info(f"Socket: Received {command} command with setting '{command_setting}' from {client_addr}")
                if self.dev_manager.is_valid_command(command):
                    priority = 5
                    if "laser" in command.lower():
                        priority = 1
                    msg_id = client_addr[0] + ':' + str(self.msg_num)
                    res = self.msg_handler(self.msg_queue, msg_id, recv_msg, priority)
                    response = res["Res_Value"]
                    response_error = res["Error"]
                    response = {"ID": msg_id, "Value": response, "Error": response_error}
                    response = json.dumps(response)
                    byte_response = bytes(response,encoding='utf-8')
                    response_len = len(byte_response)
                    response = response_len.to_bytes(2,"big") + byte_response
                    client_conn.send(response)
                else:
                    msg_id = client_addr[0] + ':' + str(self.msg_num)
                    logger.error(f"socketManager: Received invalid request of {command} from msg id {msg_id}")
                    invalid_msg = {'ID': msg_id, 'Value':None, 'Error':'Invalid command.'}
                    invalid_msg = json.dumps(invalid_msg)
                    invalid_msg_len = len(invalid_msg)
                    invalid_msg = invalid_msg_len.to_bytes(2,"big") + bytes(invalid_msg,encoding='utf-8')
                    client_conn.send(invalid_msg)
                self.msg_num += 1
                self.msg_num %= 8000


