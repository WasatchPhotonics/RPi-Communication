import socket
import threading
import matplotlib.pyplot as plt

HOST = '192.168.1.30'
PORT = 8181

def perform_socket_comm(subplt,fig):
    x = []
    y = []
    line = subplt.plot(x,y)[0]
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
                    if response is None or response.decode('utf-8') == '':
                        print('Received null response. Connection closed. Exiting.')
                        return
                    msg.append(response)
                    total_msg_received += len(response)
                    print(f"continuing response call, got message of length {len(response)} total received is {total_msg_received} of {msg_len}")
                complete_msg = b''.join(msg)
                complete_msg = complete_msg.decode('utf-8')
                print(f"Received response of {complete_msg}")
            if command.upper() == "GET_SPECTRA":
                complete_msg = complete_msg.replace('[','')
                complete_msg = complete_msg.replace(']','')
                values = complete_msg.split(',')
                filt_values = [val.replace(' ','') for val in values if val != '']
                spectra_data = [float(val) for val in filt_values if val != '']
                x = list(range(len(spectra_data)))
                y = spectra_data
                ax = fig.axes[0]
                line.set_data(x,y)
                if y != []:
                    ax.set_xlim(min(x),max(x))
                    ax.set_ylim(min(y),max(y))
                plt.draw()

fig = plt.figure()
subplt = fig.add_subplot(111)
comm_thread = threading.Thread(target=perform_socket_comm, args=(subplt,fig))
comm_thread.start()
plt.show()
