import json
import socket
import logging
import threading

logger = logging.getLogger(__name__)

class Socket_Manager:
    def __init__(self, device_manager, msg_queues):
        self.port = 8181
        self.server_name = socket.gethostbyname(socket.gethostname() + ".local")

        self.format = 'utf-8'
        self.dev_manager = device_manager
        self.msg_queues = msg_queues
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.server_name, self.port))
        self.msg_len = None
        self.msg_num = 0
        self.start()

    def start(self):
        self.server_socket.listen()
        logger.info(f"Socket: started server listening on {self.server_name} on port {self.port}")
        while True:
            client_socket, addr = self.server_socket.accept()
            client = threading.Thread(target=self.client_thread, args=(client_socket,addr))
            client.start()

    def client_thread(self, client_conn, client_addr):
        logger.info(f"Socket: Received new client connection from address {client_addr}")
        while True:
            command = client_conn.recv(1024)
            if not command:
                client_conn.close()
                logger.info("Socket: Received blank command. Closing connection")
                break
            else:
                command = command.decode(self.format)
                command = command.upper()
                command_name = command
                command_values = command.split(':')
                command_setting = ''
                if len(command_values) == 2:
                    command_name, command_setting = command_values
                if self.dev_manager.is_valid_command(command_name):
                    priority = 5
                    if "laser" in command.lower():
                        priority = 1
                    logger.info(f"Socket: Received {command} command with setting '{command_setting}' from {client_addr}, with priority {priority}")
                    msg_id = client_addr[0] + str(self.msg_num)
                    data = (msg_id, command)
                    self.msg_queues['send'].put_nowait((priority, data))
                    client_conn.send("Received your message.".encode(self.format))
                else:
                    client_conn.send("Invalid command.".encode(self.format))
                self.msg_num += 1
                self.msg_num %= 8000


