# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT


import socketpool
import wifi

import neopixel
import touchio
import json
import board
from digitalio import DigitalInOut, Direction
import time
from ledPixelsPico import *

#import microcontroller



from adafruit_httpserver import Server, Request, Response, POST

# nPix = 32
# pix = ledPixels(nPix, board.GP15)
# ledMode="rainbow"

from uNetComm import *
deviceInfo = {
    'deviceName': 'HexKeyPad',
    'notes': 'Round 7 Hex Keypad (by Blas and Ruthie)',
    'hostname': ''
    }

#  connect to network
print()
print("Connecting to WiFi")
#  connect to your SSID
wifi.radio.connect('TFS Students', 'Fultoneagles')

makerspaceServerIP = 'http://makerspace.local:27182'

with open("index.html") as f:
    webpage = f.read()

print("Connected to WiFi")
pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, "/static", debug=True)
port = 80
comm = uNetComm(pool)


# UTILITY FUNCTIONS
def requestToArray(request):
    raw_text = request.body.decode("utf8")
    print("Raw")
    data = json.loads(raw_text)
    return data

@server.route("/")
def base(request: Request):
    """
    Serve the default index.html file.
    """
    return Response(request, f"{webpage}", content_type='text/html')


led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
led.value = False
@server.route("/led", "POST")
def ledButton(request: Request):
    # raw_text = request.body.decode("utf8")
    global ledMode
    print("Raw")
    # data = json.loads(raw_text)
    data = requestToArray(request)
    print(f"data: {data} & action: {data['action']}")
    rData = {}
    
    if (data['action'] == 'ON'):
        led.value = True
        ledMode="rainbow"
        
    if (data['action'] == 'OFF'):
        led.value = False
        ledMode="OFF"
    
    rData['item'] = "led"
    rData['status'] = data['action']
    
    print("ledMode:", ledMode)
        
    return Response(request, json.dumps(rData)) 
     




def signalMksDevice(comm, ip, item, status, timeout=2):
    try: 
        data = comm.request(ip, item, status, timeout=timeout)
        print(f'data ({ip}):', data.text)
    except:
        data = None
        print(f'{ip} signal failed')
    return data





class hexFunc(object):
    def __init__(self, tGP = board.GP18, lGP = board.GP22,  color = [0,0,250], id=-1):
        self.tGP = tGP
        self.lGP = lGP
        self.ledPix = ledPixels(24, lGP)
        self.ledPix.clear()
        self.touch = touchio.TouchIn(tGP)
        self.color = color
        self.id = id
        self.beingTouched = False
        
    def Hexagon(self):
        if self.touch.value:
            self.ledPix.setColor(self.color)
        else:
            self.ledPix.clear()
            
    def touching(self):
        value = self.touch.value
        #if value:
            #print("touching", self.id)
        return value
            
    def light(self, color=None):
        if color != None:
            self.ledPix.setColor(color)  
        else:
            self.ledPix.setColor(self.color)            
        
    def off(self):
        self.ledPix.clear()
        
    def touchStart(self):
        self.beingTouched = True
        self.wasTouched = True
        self.touchStartTime = time.monotonic()
        self.light()
        print(f'start: {self.id}')
        
    def touchStop(self):
        self.beingTouched = False
        self.wasTouched = True
        self.touchStopTime = time.monotonic()
        self.off()
        print(f'stop: {self.id}, for: {self.touchStopTime-self.touchStartTime}')
        
    
    

class hexController:
    def __init__(self):
        
        self.hexes = []
        self.hexes.append(
            hexFunc(tGP=board.GP2, lGP=board.GP3, color=[250,0,0], id=len(self.hexes)))
        self.hexes.append(hexFunc(tGP=board.GP10, lGP=board.GP11, id=len(self.hexes)))
        self.hexes.append(hexFunc(tGP=board.GP12, lGP=board.GP13, id=len(self.hexes)))
        self.hexes.append(hexFunc(tGP=board.GP16, lGP=board.GP17, id=len(self.hexes)))
        self.hexes.append(hexFunc(tGP=board.GP18, lGP=board.GP19, id=len(self.hexes)))
        self.hexes.append(hexFunc(tGP=board.GP20, lGP=board.GP21, id=len(self.hexes)))
        self.hexes.append(hexFunc(tGP=board.GP14, lGP=board.GP15, id=len(self.hexes)))
        
        self.hexes[-1].hexes = self.hexes
        self.resetID = len(self.hexes)-1
        print("RESET ID: ", self.resetID)
        
        self.keySeq = []
        
    def lightAll(self, delay=0.1):
        for hex in self.hexes:
            hex.light()
            time.sleep(delay)
            
    def lightAllColor(self, color=[0,250,0], delay=0.1):
        for hex in self.hexes:
            hex.light(color)
            time.sleep(delay)
            
    def startUp(self, delay=0.1):
        self.lightAll(delay)
        self.offAll()
            
    def offAll(self):
        for hex in self.hexes:
            hex.off()
        
    def lightOnTouch(self):
        
        while True:
            for hex in self.hexes:
                if hex.touching():
                    hex.light()
                else:
                    hex.off()
                    
    def keyPad(self):
        
        
        while True:
            for hex in self.hexes:
                if hex.touching():
                    if hex.beingTouched == False:
                        hex.touchStart()
                        if hex.id == self.resetID:
                            self.lightAll()
                else:
                    if hex.beingTouched:
                        hex.touchStop()
                        self.keySeq.append(hex.id)
                        
                        if hex.id == self.resetID:
                            self.offAll()
                            
                            # key sequence actions
                            seq = ""
                            for i in self.keySeq:
                                seq += str(i)
                            print("Key Seq:", self.keySeq, seq)
                            
                            self.keySeq = []
                            
                            if seq == "056":
                                
                                if 'Icebreaker: Hexagons' in mkspDevicesIPs:
                                    signalMksDevice(comm, mkspDevicesIPs['Icebreaker: Hexagons'], "hexOn", "test")
                                
                                #signalMksDevice(comm, "http://20.1.0.179:8080/", "playSound", "powerup.wav")
                                #signalMksDevice(comm, "http://20.1.1.203/", "hexOn", "test")
                                #signalMksDevice(comm, "http://20.1.0.89:80/", "setMode", "rainbow")
                                hCon.lightAllColor(color=[0,250,0], delay=0.1)
                                
                            if seq == "436":
                                
                                if 'Icebreaker: Hexagons' in mkspDevicesIPs:
                                    signalMksDevice(comm, mkspDevicesIPs['Icebreaker: Hexagons'], "hexOff", "test")
                                
                                #signalMksDevice(comm, "http://20.1.0.179:8080/", "playSound", "powerdown.wav")
                                #signalMksDevice(comm, "http://20.1.1.203/", "hexOff", "test")
                                #signalMksDevice(comm, "http://20.1.0.89:80/", "setMode", "off")
                                hCon.lightAllColor(color=[0,0,0], delay=0.25)
                                

                        
hCon = hexController()

startTime = time.monotonic()
print("StartTime:", startTime)


print("starting server..")
# startup the server
try:
    server.start(str(wifi.radio.ipv4_address), port)
    print(f"Listening on http://{wifi.radio.ipv4_address}:{port}" )
        
#  if the server fails to begin, restart the pico w
except OSError:
    time.sleep(5)
    print("restarting..")
    microcontroller.reset()
    
# log device on makerspace network
try:
    # log device on makerspace network
    regInfo = {"ip": f'{wifi.radio.ipv4_address}:{port}',
               "deviceName": deviceInfo['deviceName'],
               "hostname": deviceInfo['hostname'],
               "notes": deviceInfo['notes']
               }
    #regData = comm.request("http://makerspace.local:27182", "registerDevice", regInfo)
    regData = comm.request(makerspaceServerIP, "registerDevice", regInfo)
    print('registered:', regData.text)
    #hCon.startUp(0.25)
    hCon.lightAllColor(color=[0,0,250], delay=0.25)
    time.sleep(1)
    hCon.offAll()
except:
    #go to local mode
    print("Failed to register to Makerspace Network")

hCon.lightAllColor(color=[0,250,0], delay=0.25)


mkspDevicesIPs = {}
# get all network devices info
try:
    deviceTable = comm.request(makerspaceServerIP, "getDeviceTable")
    print("Acquired device table.")
    dt = json.loads(deviceTable.text)
    print("loaded", dt['status'])
    print('-----')
    dt = dt['status']
    
    for item in dt:
        #print(item)
        print(item['deviceName'], " | ", item['ip'])
        mkspDevicesIPs[item['deviceName']] = 'http://' + item['ip']
    print (mkspDevicesIPs)
    
except Exception as e:
    print("ERROR:", e)
    print(f"Failed to get device table from {makerspaceServerIP}")




#hCon.lightOnTouch()
hCon.keyPad()







