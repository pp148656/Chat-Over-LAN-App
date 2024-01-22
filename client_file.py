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
from tkinter.tix import *
from email import encoders
import random
import math


class GUI:
    client_socket = None
    last_received_message = None
    
    # this function called after object creation
    def __init__(self, master):
        self.otp_ar = []
        self.root = master
        self.chat_transcript_area = None
        self.name_widget = None
        self.password_widget = None
        self.enter_text_widget = None
        self.flag = bool(1)
        self.join_button = None
        
        # intitialise sockets and makes tkinter based gui
        self.initialize_socket()
        self.initialize_gui()
        # listen for incoming messages from server
        self.listen_for_incoming_messages_in_a_thread()

    def initialize_socket(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initialazing socket with TCP and IPv4
        remote_ip = '127.0.0.1' # IP address 
        remote_port = 10319 #TCP port
        self.client_socket.connect((remote_ip, remote_port)) #connect to the remote server

    # GUI initializer
    def initialize_gui(self): 
        self.root.title("Chat App") 
        # emoticons map with specific keywords
        self.emotioncs_map = {'/Happy':'｡^‿^｡','/Dance':'~( ˘▾˘~)','/Flirt':'(‿!‿) ԅ(≖‿≖ԅ)','/Ok':'٩(•̤̀ᵕ•̤́๑)ᵒᵏᵎᵎᵎᵎ','/Confused' : 'O.o', '/Cool' : 'B-)', '/Sarcastic' : '( ͡° ͜ʖ ͡° )', '/Joy':'(づ ◕‿◕ )づ', '/Greedy':'$_$', '/Sleep':'(－_－) zzZ', '/Wow':'(ᵒ̤̑ ₀̑ ᵒ̤̑)wow!*✰'}
        # adding a menu bar
        self.menu = Menu(self.root)
        root.config(menu=self.menu)
        self.filemenu = Menu(self.menu)
        # entering new and exit buttons inside File menu button
        self.menu.add_cascade(label='File', menu=self.filemenu)
        self.filemenu.add_command(label='New', command=self.open_new_file)
        self.filemenu.add_separator()
        self.filemenu.add_command(label='Exit', command=self.on_close_window)
        self.root.resizable(0, 0)
        
        # calling all the GUI Components functions
        self.display_name_section()
        self.display_password_section()
        self.display_otp_section()
        self.display_enter_otp_section()
        self.display_new_password_section()
        self.display_chat_box()
        self.display_chat_entry_box()
        self.display_send_file_section()
        
    def display_name_section(self):
        frame = Frame()
        # welcome label
        Label(frame, text='IIT Patna Student Chat Portal',fg='#0d0d0d', font=('Cambria', 24, "underline")).pack(side='left', padx=520)
        frame.pack(side='top', anchor='nw')
        
        # email labels and entry boxes
        frame = Frame()
        Label(frame, text='Enter Your Username Here! ', font=("arial", 13,"bold")).pack(side='left', pady=20)
        self.name_widget = Entry(frame, width=60,font=("arial", 13))
        self.name_widget.pack(side='left', anchor='e',padx=123, pady=15)
        self.join_button = Button(frame, text="Join", font=("arial", 11,"bold"), width=10, command=self.on_join).pack(side='right',padx=45, pady=15)
        frame.pack(side='top', anchor='nw')
        
    def display_password_section(self):
        frame = Frame()
        # password labels and entry boxes
        Label(frame, text='Enter Your Password Here! ', font=("arial", 13,"bold")).pack(side='left')
        self.password_widget = Entry(frame, width=60,font=("arial", 13))
        self.password_widget.pack(side='left', anchor='e', padx=125, pady=1)
        self.forgot_password_button = Button(frame, text="Forgot Password",font=("arial", 11,"bold"), width=20, command=self.forgot_password).pack(side='right',padx=5, pady=1)
        frame.pack(side='top', anchor='nw')

    def display_otp_section(self):
        frame = Frame()
        # enter mail to reset your password labels and entry boxes
        Label(frame, text='Enter E-mail to Reset Your Password ', font=("arial", 13,"bold")).pack(side='left', pady=10)
        self.get_otp_widget = Entry(frame, width=60,font=("arial", 13))
        self.get_otp_widget.pack(side='left', anchor='e',padx=50, pady=10)
        self.get_otp_button = Button(frame, text="Get OTP",font=("arial", 11,"bold"), width=10, command=self.send_otp).pack(side='right',padx=120, pady=10)
        frame.pack(side='top', anchor='nw')        
        self.get_otp_widget.config(state='disabled')

    def display_enter_otp_section(self):
        frame = Frame()
        # otp and submit otp labels buttons, entry boxes
        Label(frame, text='Enter OTP for Password Reset ', font=("arial", 13,"bold")).pack(side='left', pady=10)
        self.enter_otp_widget = Entry(frame, width=60,font=("arial", 13))
        self.enter_otp_widget.pack(side='left', anchor='e',padx=100, pady=10)
        self.enter_otp_button = Button(frame, text="Submit OTP",font=("arial", 11,"bold"), width=10, command=self.submit_otp).pack(side='right',padx=70, pady=10)
        self.enter_otp_widget.config(state='disabled')
        frame.pack(side='top', anchor='nw')        
        
    def display_new_password_section(self):
        frame = Frame()
        # new password entry boxes, labels and Reset button
        Label(frame, text='Enter New Password for Password Reset ', font=("arial", 13,"bold")).pack(side='left', pady=20)
        self.new_password_widget = Entry(frame, width=60,font=("arial", 13))
        self.new_password_widget.pack(side='left', anchor='e',padx=20, pady=15)
        self.new_password_button = Button(frame, text="Reset Password",font=("arial", 11,"bold"), width=15, command=self.reset_password).pack(side='right',padx=120, pady=15)
        self.new_password_widget.config(state='disabled')
        frame.pack(side='top', anchor='nw')        

    def display_send_file_section(self):
        frame = Frame()
        # bottom buttons arrangement
        self.button_explore = Button(frame, text = "Send Files", width=16,fg='#000000',bg='#ffcccc',font=("Sans Serif", 15), command=self.browseFiles).pack(side='left',padx=40, pady=10)
        self.button_invite_friends = Button(frame, text = "Invite Friends", fg='#000000',bg='#ffcccc',font=("Sans Serif", 15), width=16, command=self.invite_friends_fun).pack(side='left',padx=40, pady=10)
        self.button_new_user = Button(frame, text = "Sign Up", width=16,fg='#000000',bg='#ffcccc',font=("Sans Serif", 15), command=self.open_sign_up_file).pack(side='right',padx=20, pady=10)
        Label(frame, text='New User?',font=("Sans Serif", 14, "bold")).pack(side='right',padx=10, pady=20)
        self.button_block = Button(frame, text = "Block Notifs.", width=16,fg='#000000',bg='#ffcccc',font=("Sans Serif", 15), command=self.block_chat).pack(side='left',padx=30, pady=10)
        self.button_clear_chat = Button(frame, text = "Clear Chats", width=16,fg='#000000',bg='#ffcccc',font=("Sans Serif", 15), command=self.delete_chat).pack(side='left',padx=30, pady=10)
        frame.pack(side='top', anchor='nw')        
    
    # when block chat is pressed it acts as a toggle between 0 and 1
    def block_chat(self):
        self.flag = ((self.flag)^1)
        print(self.flag)
    
    # when clear chat is pressed, it deletes chat area
    def delete_chat(self):
        self.chat_transcript_area.delete("1.0", "end")
        
    def display_chat_box(self):
        frame = Frame()
        # chat box to display chats by receiving from server
        Label(frame, text='Chat Box', fg='#660000', font=("arial", 16,"italic")).pack(side='top', padx=270)
        self.chat_transcript_area = Text(frame, width=140, height=11, font=("arial", 12))
        scrollbar = Scrollbar(frame, command=self.chat_transcript_area.yview, orient=VERTICAL)
        self.chat_transcript_area.config(yscrollcommand=scrollbar.set)
        self.chat_transcript_area.bind('<KeyPress>', lambda e: 'break')
        self.chat_transcript_area.pack(side='left', padx=15, pady=8)
        # scrollbar alignment
        scrollbar.pack(side='right', fill='y',padx=1)
        frame.pack(side='top')

    def display_chat_entry_box(self):   
        frame = Frame()
        # place to type chat, after enter key is pressed, corresoponding on_enter_key_pressed function called
        self.temp_label = Label(frame, text='Enter Your Message Here!', fg='#660000', font=("comic sans ms", 16,"italic")).pack(side='top', anchor='w', padx=450)
        self.enter_text_widget = Text(frame,bg='#e6ffff', width=130, height=2, font=("constantia", 12))
        self.enter_text_widget.pack(side='left', pady=8, padx=10)
        self.send_button = Button(frame, text="Send", width=10,command=self.on_enter_key_pressed, font=("calibri", 13,"bold")).pack(side='right',padx=20, pady=10)
        # self.enter_text_widget.bind('<Return>', self.on_enter_key_pressed)
        frame.pack(side='top')

    # when new file is clicked from menu bar
    def open_new_file(self):
        # opening file in a seperate thread, so that other process don't wait for it.
        self.thread_file = threading.Thread(target=self.open_func)
        self.thread_file.start()
    
    # opening file 
    def open_func(self):    
        os.system('python client_file.py')

    # opening sign up file in a seperate thread when signup button is pressed
    def open_sign_up_file(self):
        self.thread_file2 = threading.Thread(target=self.open_reg_file)
        self.thread_file2.start()
    
    # opening sign up file
    def open_reg_file(self):    
        os.system('python signUp_file.py')

    def browseFiles(self):
        # to send files to server
        file_path = fd.askopenfilename(initialdir = "/", title = "Select a File", filetypes = (("Text files", "*.txt*"), ("all files", "*.*")))
        file_size = os.path.getsize(file_path)
        # opened file
        with open(file_path, "rb") as file:
            c = 0

            # Running loop while c != file_size.
            while c <= file_size:
                data = file.read(1024)
                if not (data):
                    break
                c += len(data)

                # sending data of file to server with [[[ ..... ]]] this way encoding, so to uniquely determine at server's side.
                self.client_socket.send(( str(self.name_widget.get()) + " joined:" + '[[[' + str(data) + ']]]').encode('utf-8'))

    # new top tkinter GUI for person invitation, when invite to friends button is clicked
    def invite_friends_fun(self):
        self.top = Toplevel(root, width=100)
        self.label_mail = Label(self.top, text='Enter Mail id').pack()
        self.invite_btn = Button(self.top, text='Send', command=self.invite_via_mail) 
        self.invite_mail_id = Entry(self.top)
        self.invite_mail_id.pack()  
        self.invite_btn.pack()
    
    def invite_via_mail(self):
        # inviting friends via mail from another window
        FROM_ADDR = "cs384@iitp.ac.in"
        FROM_PASSWD = "changeme"
        Subject = "Chat App Invitation"
        Body = 'Your friend has invited you to join chat app. Please open the attached file code.'
        
        self.send_invitation_mail(FROM_ADDR, FROM_PASSWD,str(self.invite_mail_id.get()), Subject, Body, 'client_file.py')
        self.top.destroy()

            
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
            message = buffer.decode('utf-8')

            now = datetime.now()
            # dd/mm/YY H:M:S
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

            # receiving and decoding what to print, with the desired encodings
            print(str(message))
            # last seen notif is received
            if message[-1] == '-':
                message = user + ' was last seen at ' + dt_string
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)
            elif "[[[" in message:                              # file sent notification received
                self.msg_dis = str(message).split('[[[')[1].split(']]]')[0]
                sender_name = str(message).split(' ')[0]
                
                message = '[' + dt_string + '] : ' + sender_name + ' sent a file.'
                self.msg_dis = self.msg_dis[2:-1]
                self.file_lines = str(self.msg_dis).split('\\r\\n')
                
                # writing the file to clients storage
                with open('file_' + str(self.name_widget.get()) + '.txt', 'w') as file:
                    for i in self.file_lines:
                        file.writelines(i + '\n')
                
                file.close()
                
                # sending notif for file sent.
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)                
            elif "joined" in message:                           # joined notification received
                user = message.split(":")[1]
                message = user + " is online from " + dt_string
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)
            elif "error" in message:                            # wrong credentials notification received
                messagebox.showerror("Invalid username or Password, enter valid credentials again and press join.")
            else:                                               # normal chat message notification
                if (self.flag == 1):                    
                    self.show_msg = self.chat_emoji_decrypt(msg=message)
                    print('hello')
                    self.chat_transcript_area.insert('end', self.show_msg + '\n')
                    self.chat_transcript_area.yview(END)

        so.close()
    
    def chat_emoji_decrypt(self, msg):
        for i in self.emotioncs_map:            # checking for each emoticon if present
            print(i, msg)
            if i in str(msg):
                # inserting the respective emoticon at the desired location.
                str_indx = str(msg).index(str(i))
                lst_indx = str_indx + len(str(i)) - 1
                
                fst_part = str(msg[:str_indx])
                mid_part = str(self.emotioncs_map[i])
                lst_part = str(msg[lst_indx+1:])
                
                #modified msgs 
                return (fst_part + mid_part + lst_part)
            
        return msg                

    # mail function to send invitation mail to friends with client_file code
    def send_invitation_mail(self, fromaddr, frompasswd, toaddr, msg_subject, msg_body, file_path):
        # try block for error handling
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

        filename = file_path
        attachment = open(filename, "rb")

        p = MIMEBase('application', 'octet-stream')

        p.set_payload((attachment).read())

        encoders.encode_base64(p)

        p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

        # try block for error handling
        try:
            msg.attach(p)
            print("[+] File Attached")
        except:
            print("[-] Error in Attaching file")
            return

        # try block for error handling
        try:
            # s = smtplib.SMTP('smtp.gmail.com', 587)
            s = smtplib.SMTP('stud.iitp.ac.in', 587)
            print("[+] SMTP Session Created")
        except:
            print("[-] Error in creating SMTP session")
            return

        s.starttls()

        # try block for error handling
        try:
            s.login(fromaddr, frompasswd)
            print("[+] Login Successful")
        except:
            print("[-] Login Failed")

        text = msg.as_string()

        # try block for error handling
        try:
            s.sendmail(fromaddr, toaddr, text)
            print("[+] Mail Sent successfully")
        except:
            print('[-] Mail not sent')

        s.quit()
    
    # reset password function
    def reset_password(self):
        # sending changed password to server
        self.client_socket.send(("joined:" + self.get_otp_widget.get() + '--reset--'+ self.new_password_widget.get()).encode('utf-8'))
        self.name_widget.delete(0, END);
        self.password_widget.delete(0, END);
        self.get_otp_widget.delete(0, END);
        self.enter_otp_widget.delete(0, END);
        self.new_password_widget.delete(0, END);
        # disabling all the req text boxes after password got reset
        self.get_otp_widget.config(state='disabled')
        self.enter_otp_widget.config(state='disabled')
        self.new_password_widget.config(state='disabled')
        
    def submit_otp(self):        
        # otp checking correct or not for password resetting
        if str(self.enter_otp_widget.get()) == self.otp_ar[len(self.otp_ar)-1]:
            self.new_password_widget.config(state='normal')
        else:
            messagebox.showerror("Wrong OTP entered.")

    def forgot_password(self):
        self.get_otp_widget.config(state='normal')

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
        
    def send_otp(self):
        self.enter_otp_widget.config(state='normal')
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
        
        self.otp_ar.append(random_str)
        
        FROM_ADDR = "cs384@iitp.ac.in"
        FROM_PASSWD = "changeme"
        Subject = "Chat App OTP for Password Reset"
        Body = 'Your One Time Password to Reset your password is ' + random_str
        
        self.send_mail(FROM_ADDR, FROM_PASSWD,str(self.get_otp_widget.get()), Subject, Body)
        # ------------------------------------------------------------------------------------------------------

    # called when Join button is clicked
    def on_join(self):
        if len(self.name_widget.get()) == 0:
            messagebox.showerror(
                "Enter your name", "Enter your name to send a message")
            return
        # sending info to server
        self.client_socket.send(("joined:" + self.name_widget.get() + '='+ self.password_widget.get()).encode('utf-8'))

    def on_enter_key_pressed(self):
        if len(self.name_widget.get()) == 0:
            messagebox.showerror("Enter your name", "Enter your name to send a message")
            return
        # sending chat info to server and clearing texts
        self.send_chat()
        self.clear_text()

    def clear_text(self):
        self.enter_text_widget.delete(1.0, 'end')

    def send_chat(self):
        # sending chat with current time to server
        now = datetime.now()
        # dd/mm/YY H:M:S
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        # encoding chats for sending to server
        senders_name = '[' + dt_string + '] : ' + self.name_widget.get().strip().strip() + ": "
        data = self.enter_text_widget.get(1.0, 'end').strip()
        message = (senders_name + data).encode('utf-8')
        self.chat_transcript_area.insert('end',message.decode('utf-8') + '\n')
        self.chat_transcript_area.yview(END)
        self.client_socket.send(message)
        self.enter_text_widget.delete(1.0, 'end')
        return 'break'

    def on_close_window(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            # after closing an account, following things will happen
            self.client_socket.send((self.name_widget.get() + '-').encode('utf-8'))
            self.root.destroy()
            self.client_socket.close()
            exit(0)

#the main function 
if __name__ == '__main__':
    root = Tk()
    
    # after instantiating, constructor function will be called for this class
    gui = GUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_close_window)
    root.mainloop()