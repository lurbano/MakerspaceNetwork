'''
Runs PicoW with a photoresistor and LED (neopixel) attached

'''


import socketpool
import wifi

from adafruit_httpserver.mime_type import MIMEType
from adafruit_httpserver.request import HTTPRequest
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.server import HTTPServer

import json
import board
from digitalio import DigitalInOut, Direction
import time


'''LED SETUP'''
from ledPixelsPico import *
nPix = 90

white = (255, 255, 150)
yellow = (255, 165, 0)
orange = (205, 85, 0)
green = (45, 255, 0)
red = (255, 0, 0)
seafoam = (50, 255, 50)
lightBlue = (0, 200, 255)
niceBlue = (0, 100, 255)
pureBlue = (0, 0, 255)
pastelPurple = (255, 100, 255)
purePurple = (255, 0, 255)



setcolor = pastelPurple

pix1 = ledPixels(nPix, board.GP2)
pix2 = ledPixels(nPix, board.GP10)
pix3 = ledPixels(nPix, board.GP14)

pix1.brightness = 1

pix1.rainbowForever()

pix2.brightness = 1

pix2.setColor((setcolor))

pix3.brightness = 1

pix3.setColor((setcolor))


with open("index.html") as f:
    webpage = f.read()


#ssid, password = secrets.WIFI_SSID, secrets.WIFI_PASSWORD  
ssid, password = "TFS Students", "Fultoneagles"  

print("Connecting to", ssid)
wifi.radio.connect(ssid, password)
print("Connected to", ssid)

pool = socketpool.SocketPool(wifi.radio)
server = HTTPServer(pool)


led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
led.value = False



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
    rData = {}
        
    print("POST")
    data = requestToArray(request)
    print(f"data: {data} ")
    print(f"action: {data['action']} & value: {data['value']}")

    # SET MODE
    if (data['action'] == "light1ON"):
        pix1.setColor((setcolor))
        rData['item'] = "light1ON"
        rData['status'] = f"{orange}"
    if (data['action'] == "light1OFF"):
        pix1.off()

        rData['item'] = "light2OFF"
        rData['status'] = "off"

    if (data['action'] == "light2ON"):
        pix2.setColor((setcolor))
        rData['item'] = "light2ON"
        rData['status'] = f"{orange}"
    if (data['action'] == "light2OFF"):
        pix2.off()
        
    if (data['action'] == "light3ON"):
        pix3.setColor((setcolor))
        rData['item'] = "light3ON"
        rData['status'] = f"{orange}"
    if (data['action'] == "light3OFF"):
        pix3.off()

        rData['item'] = "light2OFF"
        rData['status'] = "off"

    with HTTPResponse(request) as response:
        response.send(json.dumps(rData))

@server.route("/led", "GET")
def ledButton(request: HTTPRequest):
    rData = {}
    
    if led.value:
        led.value = False
    else:
        led.value = True
    
    rData['item'] = "onboardLED"
    rData['status'] = led.value
        
    with HTTPResponse(request) as response:
        response.send(json.dumps(rData))

@server.route("/photoResistor", "GET")
def ledButton(request: HTTPRequest):
    rData = {}
    
    rData['item'] = "photoResistor"
    rData['status'] = pr.getPercent()
    
    with HTTPResponse(request) as response:
        response.send(json.dumps(rData))

 
print(f"Listening on http://{wifi.radio.ipv4_address}:80")
# Start the server.
server.start(str(wifi.radio.ipv4_address))

while True:
    try:
        # Process any waiting requests
        server.poll()
        time.sleep(0.1)
    except OSError as error:
        print(error)
        continue

        





