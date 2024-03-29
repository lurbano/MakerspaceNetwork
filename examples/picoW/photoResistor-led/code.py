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

'''PHOTORESISTOR SETUP'''
from photoResist import *
pr = photoResist(board.A0, maxVal=30000, minVal=9000)  #GP26

'''LED SETUP'''
from ledPixelsPico import *
pix = ledPixels(1, board.GP15)

with open("index.html") as f:
    webpage = f.read()


#ssid, password = secrets.WIFI_SSID, secrets.WIFI_PASSWORD  
ssid, password = "Wifipower", "defacto1"  

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
    if (data['action'] == "lightON"):
        led.value = True
        rData['item'] = "onboardLED"
        rData['status'] = led.value
    if (data['action'] == "lightOFF"):
        led.value = False

        rData['item'] = "onboardLED"
        rData['status'] = led.value

    if (data['action']) == 'photoResistor':
        rData['item'] = "photoResistor"
        rData['status'] = pr.getPercent()

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
        pix.light(0, (250*pr.getPercent()/100, 0, 0))
        time.sleep(0.1)
    except OSError as error:
        print(error)
        continue

        





