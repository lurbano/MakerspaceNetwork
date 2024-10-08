
from tinydb import TinyDB, Query
from datetime import datetime
import os
import subprocess

dir_path = os.path.dirname(os.path.abspath(__file__))
qr_path = f'{dir_path}/qrCodes/'
print('path:', dir_path)
db_path = dir_path + '/db/'

class baseStationDB:
    def __init__(self):
        self.activeDB = TinyDB(db_path+'activeDB.json')

    def insert(self, 
               ip="", 
               deviceName="", 
               hostname="", 
               notes=""):
        id = self.activeDB.insert({'ip': ip, 'deviceName': deviceName, 'hostname': hostname, 'notes': notes, 
               'lastUpdateTime':getTimeString()})
        return id
    
    def updateLog(self, 
               ip="", 
               deviceName="", 
               hostname="", 
               notes=""):
        
        # generate qr codes
        fname = f'qrCodes/qr_{ip}.png'
        full_fname = f'{dir_path}/{fname}'
        subprocess.Popen(f'qrencode -o {full_fname} http://{ip}', shell=True)
        
        Device = Query()
        id = self.activeDB.upsert({
            'ip': ip, 
            'deviceName': deviceName, 
            'qrCode': fname, 
            'notes': notes, 
            'lastUpdateTime': getTimeString()
            }, 
            Device.deviceName == deviceName)
        
        return id
    
    def find(self, param="", value=""):
        q = Query()
        result = self.activeDB.search(q[param] == value)
        return result
    
    def removeByDeviceName(self, deviceName):
        Device = Query()
        self.activeDB.remove(Device.deviceName == deviceName)

def getTimeString():
    return datetime.now().strftime("%Y/%m/%d %H:%M:%S")

def parseTimeString(s):
    return datetime.strptime(s, "%Y/%m/%d %H:%M:%S")



# testing
if __name__ == '__main__':
    db = uDb()
    id = db.insert(ip = '20.0.0.1:80', hostname='makerspace.local', job='Base Station', notes='Base Station')
    id = db.insert(ip = '20.0.0.2:80', hostname='photoResistor.local', job='Makerspace Photoresistor', notes='Photo resistor that monitors light levels in the Makerspace')
    result = db.find('job', "Base Station")
    print(result)