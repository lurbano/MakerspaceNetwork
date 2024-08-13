
from tinydb import TinyDB, Query

db_path = './db/'

class uDb:
    def __init__(self):
        self.activeDb = TinyDB(db_path+'activeDb.json')

    def insert(self, 
               ip="", 
               deviceName="", 
               hostname="", 
               notes=""):
        id = self.activeDb.insert({'ip': ip, 'deviceName': deviceName, 'hostname': hostname, 'notes': notes})
        return id
    
    def find(self, param="", value=""):
        q = Query()
        result = self.activeDb.search(q[param] == value)
        return result


# testing
if __name__ == '__main__':
    db = uDb()
    id = db.insert(ip = '20.0.0.1:80', hostname='makerspace.local', job='Base Station', notes='Base Station')
    id = db.insert(ip = '20.0.0.2:80', hostname='photoResistor.local', job='Makerspace Photoresistor', notes='Photo resistor that monitors light levels in the Makerspace')
    result = db.find('job', "Base Station")
    print(result)