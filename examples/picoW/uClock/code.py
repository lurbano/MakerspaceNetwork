
import socketpool
import wifi

from adafruit_httpserver.mime_type import MIMEType
from adafruit_httpserver.request import HTTPRequest
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.server import HTTPServer
import adafruit_ntp

import json
import board
from digitalio import DigitalInOut, Direction
import touchio
from analogio import AnalogIn
import time
import os
import math
from ledPixelsPico import *
from uNetComm import *
from uKnob import uKnob
from uSchedule import *
from ledClock import *


# led Ring
ledMode = "clock"
modes = ["rainbow", "solidColor", "off", "sin", "clock"]
old_ledMode = ledMode
#ledPix = ledPixels(72, board.GP17)
#ledPix.brightness = 50

# touch sensor
touch = touchio.TouchIn(board.GP28)
print("Start touch", touch.value)

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

with open("index.html") as f:
    webpage = f.read()



#ssid, password = secrets.WIFI_SSID, secrets.WIFI_PASSWORD  # pylint: disable=no-member
ssid, password = "Wifipower", "defacto1"  # pylint: disable=no-member

#print("Connecting to", ssid)
#wifi.radio.connect(ssid, password)
#print("Connected to", ssid)

#pool = socketpool.SocketPool(wifi.radio)
pool = uNetConnect(ssid, password)
server = HTTPServer(pool)
# get time
#ntp = adafruit_ntp.NTP(pool, tz_offset=0)
ledPix = ledClock(board.GP17, 72, pool, True)
checkTime = True
#print("Time: ", ntp.datetime)

def requestToArray(request):
    raw_text = request.body.decode("utf8")
    print("Raw")
    data = json.loads(raw_text)
    return data

@server.route("/", "GET")
def base(request: HTTPRequest):
    """
    Serve the default index.html file.
    """
    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
        #response.send(f"{webpage()}")
        response.send(webpage)

@server.route("/", "POST")
def base(request: HTTPRequest):
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
        checkTime = True
            
        rData['item'] = "mode"
        rData['status'] = ledMode


    # SPECIFY COLOR FROM COLOR PICKER
    if (data['action'] == "setColor"):
        changeMode("solidColor")
        vals = data['value']
        modeColors[vals['id']] = vals['value']
        rData['item'] = vals['id']
        rData['status'] = vals['value']
        
    with HTTPResponse(request) as response:
        response.send(json.dumps(rData))

        



led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
led.value = False
@server.route("/led", "POST")
def ledButton(request: HTTPRequest):
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
        
    with HTTPResponse(request) as response:
        response.send(json.dumps(rData))
 
def changeMode(newMode):
    global old_ledMode, ledMode, solidColorCheck
    old_ledMode = ledMode
    ledMode = newMode
    solidColorCheck = True

def touchCheck():
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

print(f"Listening on http://{wifi.radio.ipv4_address}:80")
# Start the server.
server.start(str(wifi.radio.ipv4_address))

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
                    changeMode("clock")
                        
            
            elif ledMode == "clock":
                if checkTime:
                    clock = ledPix
                    clock.initTime()
                    checkTime = False
                    
                dtime = time.monotonic() - clock.zeroTime
                clock.now = clock.startTime.addSecs(dtime)
                #print(dtime, clock.now)
                clock.lightToTime(clock.now)
                
                if touchCheck():
                    checkTime = True
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

        







