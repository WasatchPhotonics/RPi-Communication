import re
import sys
import json
import socket
import argparse
import threading
import matplotlib.pyplot as plt

PORT = 8181

class Session_Manager:
    def attempt_conn(self, addr):
        self.address = addr
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Trying to connect to:", self.address)
        try:
            self.s.connect((self.address,PORT))
            return f"Connected to {self.address}"
        except Exception as e:
            print(f"Could not connect due to {e}")
            return "Error: could not connect"

    def attempt_deconn(self):
        try:
            self.s.close()
            return "Disconnected"
        except:
            print("Could not disconnect")
            return "Error: could not perform disconnect"

    def communicate_device_msg(self, msg_id, command, value):
        cmd_msg = {'ID':msg_id,'Command':command,'Value':value,'Error':None}
        cmd_msg = json.dumps(cmd_msg)
        try:
            if command == '':
                print("Closing connection")
                return
            else:
                self.s.send(bytes(cmd_msg,encoding='utf-8'))
                msg = []
                response = self.s.recv(4096)
                total_msg_received = len(response[2:])
                msg_len = int.from_bytes(response[:2], "big")
                msg.append(response[2:])
                while total_msg_received < msg_len:
                    response = self.s.recv(4096)
                    if response is None or response.decode('utf-8') == '':
                        print('Received null response. Connection closed. Exiting.')
                        return
                    msg.append(response)
                    total_msg_received += len(response)
                    print(f"continuing response call, got message of length {len(response)} total received is {total_msg_received} of {msg_len}")
                complete_msg = b''.join(msg)
                complete_msg = json.loads(complete_msg)
                print(complete_msg)
            return complete_msg
                            
        except Exception as e:
            return f"Error: Failed to send command due to {e}"

def execute_cli_commands(args):
    if args.ip == None:
        print("Error: You must provide the ip address of the Raspberry-Pi in order to connect to it.")
        return
    msg_num = 0
    ip_addr = socket.gethostname()
    session = Session_Manager()
    conn_status = session.attempt_conn(args.ip)
    if "Error" in conn_status:
        print(conn_status)
        return
    cmd_count = 0
    while cmd_count < 1 or args.repeat:
        if args.command == None:
            args.command = input("Enter the command to send: ")
        if args.command_value == None:
            args.command_value = input("Enter the value to send with that command: ")

        msg_id = ip_addr + str(msg_num)
        complete_msg = session.communicate_device_msg(msg_id, args.command, args.command_value)
        msg_num += 1
        msg_num %= 8000
        if args.command == '':
            break
        args.command = None
        args.command_value = None
        cmd_count += 1
    



if __name__ == "__main__":
    def create_parser():
        parser = argparse.ArgumentParser(description="Connect to a Raspberry-Pi that is communicating with a WP spectrometer.")
        parser.add_argument("--ip", type=str, help="The ip address of the Raspberry-Pi.")
        parser.add_argument("--command", type=str, help="The command to send to the Raspberry-Pi.")
        parser.add_argument("--command-value", type=str, help="The value to send with the command such as 15 with integration time")
        parser.add_argument("--repeat", "-r", action='store_true', help="Continue to ask the user for commands until they provide a balnk command.")
        return parser

    parser = create_parser()
    args = parser.parse_args(sys.argv[1:])
    execute_cli_commands(args)



