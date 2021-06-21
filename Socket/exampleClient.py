import socket

HOST = '192.168.1.30'
PORT = 8181

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST,PORT))
    while True:
        command = input("Type the command you wish to send to the ")
        if command == '':
            print("Closing connection")
            break
        else:
            s.send(command.encode('utf-8'))
            msg = []
            response = s.recv(4096)
            total_msg_received = len(response[2:])
            msg_len = int.from_bytes(response[:2], "big")
            msg.append(response[2:])
            while total_msg_received < msg_len:
                response = s.recv(4096)
                msg.append(response)
                total_msg_received += len(response)
                print(f"continuing response call, got message of length {len(response)} total received is {total_msg_received} of {msg_len}")
            complete_msg = b''.join(msg)
            complete_msg.decode('utf-8')
            print(f"Received response of {complete_msg}")

