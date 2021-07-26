import json
import socket
import threading
import tkinter as tk
from queue import Queue
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from exampleClient import Session_Manager
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

PORT = 8181

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        # This grid command is needed for the buttons to layout properly. It does not make sense to me why though
        # All examples make me think there only needs to be a object.gird placelement
        self.grid(row=0,column=1,columnspan=2,rowspan=2)
        self.master.grid_columnconfigure(0, weight=1)
        self.active_x = []
        self.active_y = []
        self.command_q = Queue()
        self.session = None
        self.create_widget()
        self.msg_num = 0
        self.ip_addr = socket.gethostname()

    def create_widget(self):
        self.response_value = tk.StringVar()
        self.response_error = tk.StringVar()
        self.info_msg = tk.StringVar()
        
        self.command_input = tk.Entry(self.master)
        self.value_input = tk.Entry(self.master)
        self.ip_input = tk.Entry(self.master)
        self.conn_btn = tk.Button(self.master)
        self.deconn_btn = tk.Button(self.master)
        self.command_btn = tk.Button(self.master)
        self.conn_btn["text"] = "Connect"
        self.deconn_btn["text"] = "Disconnect"
        self.command_btn["text"] = "Send"
        self.conn_btn["command"] = self.conn_socket
        self.deconn_btn["command"] = self.deconn_socket
        self.command_btn["command"] = self.perform_socket_comm
        self.active_fig = Figure(figsize = (5, 5), dpi = 100)
        self.active_plot = self.active_fig.add_subplot(111)
        self.writing_aggregate_output = ''
        self.active_line = self.active_plot.plot(self.active_x,self.active_y)[0]
        self.canvas = FigureCanvasTkAgg(self.active_fig, master = self.master) 
        self.command_label = tk.Label(self.master,text="Command:")
        self.value_label = tk.Label(self.master,text="Value:")
        self.ip_label = tk.Label(self.master,text="RPi IP:")
        self.response_value_text = tk.Label(self.master, textvariable=self.response_value)
        self.response_error_text = tk.Label(self.master, textvariable=self.response_error)
        self.info_msg_text = tk.Label(self.master, textvariable=self.info_msg)
        self.response_value.set("Response Value:")
        self.response_error.set("Response Error:")
        self.info_msg.set("Info:")

        self.canvas.draw()

        self.master.columnconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=3)
        self.master.columnconfigure(2, weight=3)
        self.info_msg_text.grid(row = 0, column = 0)
        self.ip_label.grid(row = 1, column = 0)
        self.ip_input.grid(row = 1, column = 1, sticky="")
        self.conn_btn.grid(row = 2, column = 0)
        self.deconn_btn.grid(row = 2, column = 1)
        self.canvas.get_tk_widget().grid(row = 3, column = 0, columnspan = 2, padx = 2, pady = 2)
        self.command_label.grid(row = 4, column = 0, sticky='W')
        self.command_input.grid(row = 4, column = 1, sticky='WE')
        self.value_label.grid(row = 5, column = 0, sticky='W')
        self.value_input.grid(row = 5, column = 1, sticky='WE')
        self.response_value_text.grid(row = 6, column = 0)
        self.response_error_text.grid(row = 7, column = 0)
        self.command_btn.grid(row = 8, column = 1, sticky='E')

    def conn_socket(self):
        address = self.ip_input.get()
        self.session = Session_Manager()
        conn_status = self.session.attempt_conn(address)
        self.info_msg.set(conn_status)
        if "Error" in conn_status:
            self.session = None

    def deconn_socket(self):
        print("try to disconnect")
        deconn_status = self.session.attempt_deconn()
        self.info_msg.set(deconn_status)
        if "Error" not in deconn_status:
            self.session = None

    def perform_socket_comm(self):
        fig = self.active_fig
        subplt = self.active_plot
        command = self.command_input.get()
        value = self.value_input.get()
        msg_id = self.ip_addr+str(self.msg_num)
        complete_msg = self.session.communicate_device_msg(msg_id, command, value)
        if command.upper() == "GET_SPECTRA":
            complete_msg_value = complete_msg['Value']
            spectra_data = [float(val) for val in complete_msg_value if val != '']
            self.active_x = list(range(len(spectra_data)))
            self.active_y = spectra_data
            ax = self.canvas.figure.axes[0]
            self.active_line.set_data(self.active_x,self.active_y)
            if self.active_y != []:
                ax.set_xlim(min(self.active_x),max(self.active_x))
                ax.set_ylim(min(self.active_y),max(self.active_y))
            self.canvas.draw_idle()
        else:
            complete_msg = dict(complete_msg)
            self.response_value.set(f"Response Value: {complete_msg['Value']}")
        self.response_error.set(f"Response Error: {complete_msg['Error']}")
        self.msg_num += 1
        self.msg_num %= 8000

root = tk.Tk()
root.title("Example Client")
root.minsize(500,650)
app = Application(master=root)
app.mainloop()
