from tkinter import Tk, Frame, Scrollbar, Label, END, Entry, Text, VERTICAL, Button, messagebox #Tkinter Python Module for GUI  
import socket #Sockets for network connection
from tkinter import*
import threading # for multiple proccess 
from datetime import datetime
from tkinter import filedialog as fd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from email.mime.base import MIMEBase
from email import encoders
import random
import math

class GUI:
    client_socket = None
    last_received_message = None
    
    # this function called after object creation
    def __init__(self, master):
        self.root = master
        self.mail_str = ''
        self.cur_otp = ''
        self.name_widget = None
        self.password_widget = None
        self.join_button = None
        
        # intitialise sockets and makes tkinter based gui
        self.initialize_socket()
        self.initialize_gui()
        self.listen_for_incoming_messages_in_a_thread()

    def listen_for_incoming_messages_in_a_thread(self):
        # Create a thread for the send and receive in same time
        thread = threading.Thread(target=self.receive_message_from_server, args=(self.client_socket,))  
        thread.start()
        
    #function to recieve msg
    def receive_message_from_server(self, so):
        while True:
            buffer = so.recv(256)
            if not buffer:
                break
            self.message = buffer.decode('utf-8')
        so.close()

    def initialize_socket(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initialazing socket with TCP and IPv4
        remote_ip = '127.0.0.1' # IP address 
        remote_port = 10319 #TCP port
        self.client_socket.connect((remote_ip, remote_port)) #connect to the remote server

    # GUI initializer
    def initialize_gui(self): 
        self.root.title("Sign Up") 
        self.root.resizable(200, 400)        
        # calling all the GUI Components functions
        self.display_name_section()
        self.display_password_section()
        self.display_email_section()

    def display_email_section(self):
        # email labels and entry boxes
        frame = Frame()
        Label(frame, text='Enter Your E-mail Here! ', font=("arial", 13,"bold")).pack(side='left', pady=20)
        self.mail_widget = Entry(frame, width=60,font=("arial", 13))
        self.mail_widget.pack(side='left', anchor='e',padx=170, pady=15)
        frame.pack(side='top', anchor='nw')        

        frame1= Frame()
        self.register_button = Button(frame1, text="Register", width=10, command=self.on_register).pack(side='right',padx=500, pady=15)
        frame1.pack(side='top', anchor='nw')     

        frame2 = Frame()
        Label(frame2, text='Enter the OTP Sent on Mail.', font=("arial", 13,"bold")).pack(side='left', pady=20)
        self.otp_widget = Entry(frame2, width=60,font=("arial", 13))
        self.otp_widget.pack(side='left', anchor='e',padx=140, pady=15)
        frame2.pack(side='top', anchor='nw') 
        self.otp_widget.config(state='disabled')
        
        frame1= Frame()
        self.submit_otp_button = Button(frame1, text="Submit OTP", width=12, command=self.on_otp_submit).pack(side='right',padx=500, pady=15)
        frame1.pack(side='top', anchor='nw')       
        pass
        
    def display_name_section(self):
        frame = Frame()
        # welcome label
        Label(frame, text='Sign Up',fg='#00008B', font=('Copperplate Gothic Bold', 20)).pack(side='left', padx=520)
        frame.pack(side='top', anchor='nw')
        
        # email labels and entry boxes
        frame = Frame()
        Label(frame, text='Enter Your Username Here! ', font=("arial", 13,"bold")).pack(side='left', pady=20)
        self.name_widget = Entry(frame, width=60,font=("arial", 13))
        self.name_widget.pack(side='left', anchor='e',padx=140, pady=15)
        frame.pack(side='top', anchor='nw')

    def display_password_section(self):
        frame = Frame()
        # password labels and entry boxes
        Label(frame, text='Enter Your Password Here! ', font=("arial", 13,"bold")).pack(side='left')
        self.password_widget = Entry(frame, width=60,font=("arial", 13))
        self.password_widget.pack(side='left', anchor='e', padx=140, pady=1)
        frame.pack(side='top', anchor='nw')

    # called when Join button is clicked
    def on_register(self):
        if len(self.name_widget.get()) == 0:
            messagebox.showerror(
                "Enter your name", "Enter your name to send a message")
            return
        self.otp_widget.config(state='normal')
        self.name_widget.config(state='disabled')
        self.password_widget.config(state='disabled')
        self.mail_widget.config(state='disabled')

        self.send_otp()
    
    # otp validation
    def on_otp_submit(self):
        if str(self.otp_widget.get()) == self.cur_otp:                  # otp entered is correct.
            messagebox.showinfo("Registered Successfully", "Proceed to Sign In :)")
            self.otp_widget.config(state='disabled')
            self.client_socket.send((self.name_widget.get() + '--pass--'+ self.password_widget.get() + '--mail--' + self.mail_widget.get()).encode('utf-8'))
        else:
            messagebox.showerror("Wrong OTP entered.")        

    def send_otp(self):
        self.otp_widget.config(state='normal')
        # generating Random OTP of 6 digits
        
        #-------------------------------------- email sending code----------------------------------------------
        ## storing strings in a list
        digits = [i for i in range(0, 10)]
        random_str = ""

        ## we can generate any lenght of string we want
        for i in range(6):
        ## generating a random index
            index = math.floor(random.random() * 10)

            random_str += str(digits[index])
        
        self.cur_otp = random_str
        
        FROM_ADDR = "ravi_2001ee53@iitp.ac.in"
        FROM_PASSWD = "Ravibihtaiit@1$"
        Subject = "Welcome to Chat App"
        Body = 'Your One Time Password for registering to the Chat app is is ' + random_str
        
        self.send_mail(FROM_ADDR, FROM_PASSWD,str(self.mail_widget.get()), Subject, Body)
        # ------------------------------------------------------------------------------------------------------

    def on_close_window(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):                          # if Ok clicked on message box
            # after closing an account, following things will happen
            self.client_socket.send((self.name_widget.get() + '-').encode('utf-8'))
            self.root.destroy()
            self.client_socket.close()
            exit(0)

    # mail format for otp sending to mail.
    def send_mail(self, fromaddr, frompasswd, toaddr, msg_subject, msg_body):
        try:
            msg = MIMEMultipart()
            print("[+] Message Object Created")
        except:
            print("[-] Error in Creating Message Object")
            return

        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = msg_subject
        body = msg_body
        msg.attach(MIMEText(body, 'plain'))
        try:
            #s = smtplib.SMTP('smtp.gmail.com', 587)
            s = smtplib.SMTP('stud.iitp.ac.in', 587)
            print("[+] SMTP Session Created")
        except:
            print("[-] Error in creating SMTP session")
            return
        s.starttls()
        try:
            s.login(fromaddr, frompasswd)
            print("[+] Login Successful")
        except:
            print("[-] Login Failed")
        text = msg.as_string()
        try:
            s.sendmail(fromaddr, toaddr, text)
            print("[+] Mail Sent successfully")
        except:
            print('[-] Mail not sent')
        s.quit()

#the main function 
if __name__ == '__main__':
    root = Tk()
    
    # after instantiating, constructor function will be called for this class
    gui = GUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_close_window)
    root.mainloop()