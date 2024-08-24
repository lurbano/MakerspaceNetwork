
import socketpool
import wifi

import json
import board
from digitalio import DigitalInOut, Direction
import touchio
from analogio import AnalogIn
import time
import os
import math
from ledPixelsPico import *
from uKnob import uKnob
from adafruit_httpserver import Server, Request, Response, POST

from uNetComm import *
deviceInfo = {
    'deviceName': 'Prusa 2 Light',
    'notes': "LED strip lighting the Prusa 2 platform.",
    'hostname': ''
    }

#  connect to network
print()
print("Connecting to WiFi")
#  connect to your SSID
wifi.radio.connect('Wifipower', 'defacto1')

with open("index.html") as f:
    webpage = f.read()

print("Connected to WiFi")
pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, "/static", debug=True)
port = 80
comm = uNetComm(pool)


# led Ring
ledMode = "rainbow"
modes = ["rainbow", "solidColor", "off", "sin"]
old_ledMode = ledMode
ledPix = ledPixels(90, board.GP2)
#ledPix.brightness = 50

# brightness Knob
brightness = 1.0
#brightKnob = uKnob(board.A1)
l_lightsON = True

solidColor = '#2ec27e'
currentSolidColor = (0,0,0)
solidColorCheck = True
modeColors = {}
modeColors["solidColor"] = solidColor
modeColors["white"] = '#f6d32d'
modeColors["red"] = (255,0,0)
modeColors["blue"] = '#2ec27e'

# sin
freq = 1
phase = 0
dp = 0.0001
sinColor = '#2ec27e'

# touch sensor
touchSensor = False
if touchSensor:
    touch = touchio.TouchIn(board.GP16)
    print("Start touch", touch.value)
    
    

def requestToArray(request):
    raw_text = request.body.decode("utf8")
    print("Raw")
    data = json.loads(raw_text)
    return data


@server.route("/")
def base(request: Request):  # pylint: disable=unused-argument
    #  serve the HTML f string
    #  with content type text/html
    return Response(request, f"{webpage}", content_type='text/html')


@server.route("/", "POST")
def base(request: Request):
    """
    Serve the default index.html file.
    """
    global ledMode
    global old_ledMode
    global modeColors
    rData = {}
        
    print("POST")
    data = requestToArray(request)
    print(f"data: {data} ")
    print(f"action: {data['action']} & value: {data['value']}")

    # SET MODE
    if (data['action'] == "lightToggle"):
        
        if ledMode == "off":
            ledMode = old_ledMode
        else:
            changeMode("off")
            
        rData['item'] = "mode"
        rData['status'] = ledMode


    if (data['action'] == "setMode"):
        
        print("IN \setmode")
        changeMode(data['value'])
        print("ledMode:", ledMode)
        #solidColorCheck = True
            
        rData['item'] = "mode"
        rData['status'] = ledMode


    # SPECIFY COLOR FROM COLOR PICKER
    if (data['action'] == "setColor"):
        changeMode("solidColor")
        vals = data['value']
        modeColors[vals['id']] = vals['value']
        rData['item'] = vals['id']
        rData['status'] = vals['value']
        
    return Response(request, json.dumps(rData))

        



led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
led.value = False
@server.route("/led", "POST")
def ledButton(request: Request):
    # raw_text = request.body.decode("utf8")
    print("Raw")
    # data = json.loads(raw_text)
    data = requestToArray(request)
    print(f"data: {data} & action: {data['action']}")
    rData = {}
    
    if (data['action'] == 'ON'):
        led.value = True
        
    if (data['action'] == 'OFF'):
        led.value = False
    
    rData['item'] = "led"
    rData['status'] = led.value
        
    return Response(request, json.dumps(rData))
 
def changeMode(newMode):
    global old_ledMode, ledMode, solidColorCheck
    old_ledMode = ledMode
    ledMode = newMode
    solidColorCheck = True

def touchCheck():
    if touchSensor:
        if touch.value:
            while touch.value:
                time.sleep(0.1)
            return True
        else:
            return False
    
def setBrightness():
    brightness = brightKnob.getPercent()/100
    if brightness < 0.02:
        ledPix.off()
        l_lightsON = False
    else:
        l_lightsON = True
        ledPix.brightness = brightness


print("starting server..")
# startup the server
try:
    server.start(str(wifi.radio.ipv4_address), port)
    print(f"Listening on http://{wifi.radio.ipv4_address}:{port}" )
    # log device on makerspace network
    regInfo = {"ip": f'{wifi.radio.ipv4_address}:{port}',
               "deviceName": deviceInfo['deviceName'],
               "hostname": deviceInfo['hostname'],
               "notes": deviceInfo['notes']
               }
    regData = comm.request("http://makerspace.local:27182", "registerDevice", regInfo)
    print('registered:', regData.text)
        

#  if the server fails to begin, restart the pico w
except OSError:
    time.sleep(5)
    print("restarting..")
    microcontroller.reset()


while True:
    try:
        '''
            LEDs
        '''
        
        #brightness = brightKnob.getPercent()/100
        #print(brightness)
        if brightness < 0.02:
            ledPix.off()
        else:
            ledPix.brightness = brightness
                        
            if ledMode == "rainbow":
                # rainbow
                for j in range(255):
                    for i in range(ledPix.nPix):
                        #setBrightness()
                        pixel_index = (i * 256 // ledPix.nPix) + j
                        
                        ledPix.pixels[i] = ledPix.wheel(pixel_index & 255, 0.5) 
                    if l_lightsON:
                        ledPix.pixels.show()
                    server.poll()
                    if ledMode == "rainbow":
                        time.sleep(0.01)
                        # check brightness dial
                        #ledPix.brighness = brightKnob.getPercent()/100
                        
                    else:
                        break
                    
                    if touchCheck():
                        changeMode("sin")
                        
            elif ledMode == "sin":
                phase += dp
                ledPix.sin(freq, phase, col=sinColor)
                ledPix.show()
                if touchCheck():
                        changeMode("solidColor")
                        
            elif ledMode in modeColors.keys():
                if modeColors[ledMode] != currentSolidColor or solidColorCheck:
                    solidColorCheck = False
                    ledPix.lightAll(modeColors[ledMode])
                    currentSolidColor = modeColors[ledMode]
                server.poll()
                if touchCheck():
                    changeMode("off")
                        
            
            elif ledMode == "off":
                ledPix.off()
                
                if touchCheck():
                        changeMode("rainbow")
                        
                        
            else:
                changeMode("off")
        # Process any waiting requests
        server.poll()
    except OSError as error:
        print(error)
        continue

        
