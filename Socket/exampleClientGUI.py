import json
import socket
import platform
import threading
import tkinter as tk
if platform.system() == 'Darwin':
    import tkmacosx as tkm #regular tkinter has issues and can't change mac button color, so need this
from queue import Queue
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from exampleClient import Session_Manager
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

PORT = 8181

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master

        self.create_pos_frames()
        self.create_widget_frames()
        self.is_mac = platform.system() == 'Darwin'

        self.active_x = []
        self.active_y = []
        self.laser_status = 0
        self.command_q = Queue()
        self.session = None
        self.create_widgets()
        self.msg_num = 0
        self.ip_addr = socket.gethostbyname("")

    def create_pos_frames(self):
        self.master.grid_columnconfigure(0, weight=1)

        self.display_frame = tk.Frame(self.master,bg='#383838')
        self.display_frame.grid(row=0,column=0,sticky='nsew')
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        self.control_frame = tk.Frame(self.master,bg='#383838',bd=3)
        self.control_frame.grid(row=0,column=1,sticky='nsew')

        self.display_top = tk.Frame(self.display_frame,bg='#383838')
        self.display_top.pack(fill=tk.X,side=tk.TOP)

        self.display_center = tk.Frame(self.display_frame,bg='#383838')
        self.display_center.pack(fill=tk.BOTH,expand=True)

        self.display_bottom = tk.Frame(self.display_frame,bg='#383838')
        self.display_bottom.pack(fill=tk.X)

    def create_widget_frames(self):
        self.conn_ip_frame = tk.Frame(self.control_frame,bd=2,bg='#212121')
        self.conn_ip_frame.pack(side=tk.TOP,fill=tk.X,padx=5,pady=5)

        self.int_frame = tk.Frame(self.control_frame,bd=2,bg='#212121')
        self.int_frame.pack(side=tk.TOP,fill=tk.X,padx=5,pady=5)

        self.gain_frame = tk.Frame(self.control_frame,bd=2,bg='#212121')
        self.gain_frame.pack(side=tk.TOP,fill=tk.X,padx=5,pady=5)

        self.laser_frame = tk.Frame(self.control_frame,bd=2,bg='#212121')
        self.laser_frame.pack(side=tk.TOP,fill=tk.X,padx=5,pady=5)

        self.capture_frame = tk.Frame(self.control_frame,bd=2,bg='#212121')
        self.capture_frame.pack(side=tk.TOP,fill=tk.X,padx=5,pady=5)

        self.gen_cmd_frame = tk.Frame(self.control_frame,bd=2,bg='#212121')
        self.gen_cmd_frame.pack(fill=tk.X,padx=5,pady=5)

    def fill_int_widget(self):
        self.int_var = tk.DoubleVar(value=0)
        self.int_label = tk.Label(self.int_frame,text="Integration Time",bg='#212121',fg='#f0f0f0')
        self.int_spin = tk.Spinbox(self.int_frame,textvariable=self.int_var,bg='#454545',fg='#f0f0f0',from_=0,to=15000,insertbackground='#f0f0f0',command=self.set_int_time)

        self.int_label.pack(side=tk.TOP,fill=tk.X,padx=5)
        self.int_spin.pack(fill=tk.X,padx=5,pady=10)

    def fill_gain_widget(self):
        self.gain_var = tk.DoubleVar(value=0)
        self.gain_label = tk.Label(self.gain_frame,text="Gain",bg='#212121',fg='#f0f0f0')
        self.gain_spin = tk.Spinbox(self.gain_frame,textvariable=self.gain_var,bg='#454545',fg='#f0f0f0',from_=0,to=15000,insertbackground='#f0f0f0',command=self.set_gain)

        self.gain_label.pack(fill=tk.X,padx=5)
        self.gain_spin.pack(fill=tk.X,padx=5,pady=10)

    def fill_laser_widget(self):
        if self.is_mac:
            self.laser_btn = tkm.Button(self.laser_frame,bg='#454545',fg='#f0f0f0',borderless=1)
        else:
            self.laser_btn = tk.Button(self.laser_frame,bg='#454545',fg='#f0f0f0')
        self.laser_btn.pack(fill=tk.X,padx=10,pady=10)
        self.laser_btn['text'] = u"\u263C Toggle Laser"
        self.laser_btn['command'] = self.toggle_laser

    def fill_capture_frame(self):
        if self.is_mac:
            self.capture_btn = tkm.Button(self.capture_frame,bg='#454545',fg='#f0f0f0',borderless=1)
        else:
            self.capture_btn = tk.Button(self.laser_frame,bg='#454545',fg='#f0f0f0')
        self.capture_btn.pack(fill=tk.X,padx=10,pady=10)
        self.capture_btn['text'] = u"\u223F Capture Spectra"
        self.capture_btn['command'] = self.capture_spectra

    def fill_conn_ip_frame(self):
        self.ip_val_frame = tk.Frame(self.conn_ip_frame,bg='#212121')
        self.ip_btn_frame = tk.Frame(self.conn_ip_frame,bg='#212121')

        self.ip_label = tk.Label(self.ip_val_frame,text="RPi IP:",bg='#212121',fg='#f0f0f0')
        self.ip_input = tk.Entry(self.ip_val_frame,bg='#454545',fg='#f0f0f0',insertbackground='#f0f0f0')

        if self.is_mac:
            self.conn_btn = tkm.Button(self.ip_btn_frame,bg='#454545',fg='#f0f0f0',borderless=1)
            self.deconn_btn = tkm.Button(self.ip_btn_frame,bg='#454545',fg='#f0f0f0',borderless=1)
        else:
            self.conn_btn = tk.Button(self.ip_btn_frame,bg='#454545',fg='#f0f0f0')
            self.deconn_btn = tk.Button(self.ip_btn_frame,bg='#454545',fg='#f0f0f0')
        self.conn_btn["text"] = "Connect"
        self.deconn_btn["text"] = "Disconnect"

        self.ip_val_frame.pack(fill=tk.X,padx=5,pady=2)
        self.ip_btn_frame.pack(fill=tk.X,pady=5)
        self.ip_label.grid(row=0,column=0)
        self.ip_input.grid(row=0,column=1)
        self.conn_btn.pack(fill=tk.X)
        self.deconn_btn.pack(fill=tk.X)

        self.conn_btn["command"] = self.conn_socket
        self.deconn_btn["command"] = self.deconn_socket

    def fill_gen_cmd_widget(self):
        self.gen_top = tk.Frame(self.gen_cmd_frame,bg='#212121')
        self.gen_ctr = tk.Frame(self.gen_cmd_frame,bg='#212121')
        self.gen_btm = tk.Frame(self.gen_cmd_frame,bg='#212121')

        self.gen_label = tk.Label(self.gen_top,text="General Command",bg='#212121',fg='#f0f0f0')
        self.command_label = tk.Label(self.gen_ctr,text="CMD:",bg='#212121',fg='#f0f0f0')
        self.value_label = tk.Label(self.gen_ctr,text="VAL:",bg='#212121',fg='#f0f0f0')
        self.command_input = tk.Entry(self.gen_ctr,bg='#454545',fg='#f0f0f0',insertbackground='#f0f0f0',bd=0)
        self.value_input = tk.Entry(self.gen_ctr,bg='#454545',fg='#f0f0f0',insertbackground='#f0f0f0',bd=0)
        if self.is_mac:
            self.command_btn = tkm.Button(self.gen_btm,bg='#454545',fg='#f0f0f0',borderless=1)
        else:
            self.command_btn = tk.Button(self.gen_btm,bg='#454545',fg='#f0f0f0')
        self.command_btn["command"] = self.perform_socket_comm
        self.command_btn["text"] = "Send"

        self.gen_top.pack(fill=tk.X)
        self.gen_label.pack(fill=tk.X)

        self.gen_ctr.pack(fill=tk.X)
        self.command_label.grid(row=0,column=0)
        self.command_input.grid(row=0,column=1)
        self.value_label.grid(row=1,column=0)
        self.value_input.grid(row=1,column=1)

        self.gen_btm.pack(fill=tk.X)
        self.command_btn.pack()

    def create_graph_widget(self):
        self.active_fig = Figure(figsize = (5, 5), dpi = 100, facecolor='#212121')
        self.active_plot = self.active_fig.add_subplot(111)
        self.ax = self.active_fig.gca()
        self.ax.spines['bottom'].set_color('#f0f0f0')
        self.ax.spines['top'].set_color('#212121') 
        self.ax.spines['right'].set_color('#212121')
        self.ax.spines['left'].set_color('#f0f0f0')
        self.ax.tick_params(axis='x', colors='#f0f0f0')
        self.ax.tick_params(axis='y', colors='#f0f0f0')
        self.ax.yaxis.label.set_color('#f0f0f0')
        self.ax.xaxis.label.set_color('#f0f0f0')
        self.ax.set_facecolor('#000')
        self.active_line = self.active_plot.plot(self.active_x,self.active_y)[0]
        self.canvas = FigureCanvasTkAgg(self.active_fig,master=self.display_center) 

    def set_gain(self,*args):
        self.perform_socket_comm('SET_GAIN',self.gain_spin.get())

    def set_int_time(self, *args):
        self.perform_socket_comm('SET_INT_TIME',self.int_spin.get())

    def capture_spectra(self):
        self.perform_socket_comm('GET_SPECTRA','0')

    def toggle_laser(self):
        if self.laser_status == 1:
            self.laser_status = 0
            self.perform_socket_comm('SET_LASER','0')
            self.laser_btn.configure(bg='#454545')
        else:
            self.laser_status = 1
            res = self.perform_socket_comm('SET_LASER','1')
            if res:
                self.laser_btn.configure(bg='red')

    def create_widgets(self):
        self.response_value = tk.StringVar()
        self.response_error = tk.StringVar()
        self.info_msg = tk.StringVar()

        self.fill_int_widget()
        self.fill_gen_cmd_widget()
        self.fill_conn_ip_frame()
        self.fill_laser_widget()
        self.fill_capture_frame()
        self.fill_gain_widget()
        self.create_graph_widget()
        
        self.writing_aggregate_output = ''
        self.response_value_text = tk.Label(self.display_bottom, textvariable=self.response_value,anchor='w',bg='#212121',fg='#f0f0f0')
        self.response_error_text = tk.Label(self.display_bottom, textvariable=self.response_error,anchor='w',bg='#212121',fg='#f0f0f0')
        self.info_msg_text = tk.Label(self.display_top,textvariable=self.info_msg,bg='#212121',fg='#f0f0f0')
        self.response_value.set("Response Value:")
        self.response_error.set("Response Error:")
        self.info_msg.set("Info:")

        self.canvas.draw()

        self.info_msg_text.pack(fill=tk.X)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH,expand=True)
        self.response_value_text.pack(fill=tk.X)
        self.response_error_text.pack(fill=tk.X)

    def conn_socket(self):
        address = self.ip_input.get()
        self.session = Session_Manager()
        conn_status = self.session.attempt_conn(address)
        self.info_msg.set(f"{conn_status}")
        if "Error" in conn_status:
            self.session = None
        else:
            self.conn_btn.configure(bg='green')
            self.perform_socket_comm('SET_LASER',0)
            int_time = self.perform_socket_comm('GET_INT_TIME',0)
            gain = self.perform_socket_comm('GET_GAIN',0)
            self.int_var.set(int_time)
            self.gain_var.set(gain)

    def deconn_socket(self):
        print("try to disconnect")
        deconn_status = self.session.attempt_deconn()
        self.info_msg.set(deconn_status)
        self.conn_btn.configure(bg='#454545')
        if "Error" not in deconn_status:
            self.session = None

    def perform_socket_comm(self,command=None,value=None):
        fig = self.active_fig
        if command is None:
            command = self.command_input.get()
        if value is None:
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
        return complete_msg['Value']

root = tk.Tk()
root.title("Example Client")
app = Application(master=root)
app.mainloop()
