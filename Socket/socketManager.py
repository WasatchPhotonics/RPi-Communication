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
        self.dev_manger = device_manager
        self.msg_queues = msg_queues
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.server_name, self.port))
        self.msg_len = None
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
                command_values = command.split(',')
                if len(command_values) == 2:
                    command, priority = command_values
                else:
                    priority = 5
                logger.info(f"Socket: Received {command} command from {client_addr}, with priority {priority}")
                client_conn.send("Received your message.".encode(self.format))


