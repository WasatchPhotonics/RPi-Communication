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
            response = s.recv(4096)
            print(f"Received response of {response}")

