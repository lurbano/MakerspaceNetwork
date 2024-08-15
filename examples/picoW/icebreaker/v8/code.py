
import socketpool
import wifi

# from adafruit_httpserver.mime_types import MIMETypes as MIMEType
# from adafruit_httpserver.request import Request as HTTPRequest
# from adafruit_httpserver.response import Response as HTTPResponse
# from adafruit_httpserver.server import Server as HTTPServer

from adafruit_httpserver.mime_type import MIMEType
from adafruit_httpserver.request import HTTPRequest
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.server import HTTPServer

import json
import board
from digitalio import DigitalInOut, Direction
import time

from cHex import *
ts = tileset()
lightSwitch = "on"
lightSwitchOld = "off"

with open("index.html") as f:
    webpage = f.read()


#ssid, password = secrets.WIFI_SSID, secrets.WIFI_PASSWORD  # pylint: disable=no-member
ssid, password = "TFS Students", "Fultoneagles"  # pylint: disable=no-member

print("Connecting to", ssid)
wifi.radio.connect(ssid, password)
print("Connected to", ssid)

pool = socketpool.SocketPool(wifi.radio)
server = HTTPServer(pool)

'''To communicate to other devices on MakerspaceNetwork use uNetComm'''
# from uNetComm import *
# comm = uNetComm(pool)
''' Request example:
comm.request("http://20.1.0.96:80", "photoResistor")
'''

led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
led.value = False



def requestToArray(request):
    raw_text = request.body.decode("utf8")
    print("Raw")
    try:
        data = json.loads(raw_text)
    except:
        print()
        print("Unable to convert request to object: requestToArray()")
        print()
        data = {}
        data["action"] = ""
        data["value"] = ""
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
        
    if (data['action'] == "hexOn"):
        global lightSwitch
        lightSwitch = 'on'

        rData['item'] = "hexLight"
        rData['status'] = lightSwitch
        
    if (data['action'] == "hexOff"):
        global lightSwitch
        lightSwitch = 'off'

        rData['item'] = "hexLight"
        rData['status'] = lightSwitch

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

 
print(f"Listening on http://{wifi.radio.ipv4_address}:80")
# Start the server.
server.start(str(wifi.radio.ipv4_address))

while True:
    try:
        # Process any waiting requests
        server.poll()
        #print(lightSwitch)
        if (lightSwitch != lightSwitchOld):
            
            lightSwitchOld = lightSwitch
            
            if lightSwitch == 'on':
                ts.firstCircle((0,0,200))
                ts.secondRing((0,100,0))
                ts.lastRing((100,0,0))
            elif lightSwitch == 'off':
                ts.firstCircle((0,0,0))
                ts.secondRing((0,0,0))
                ts.lastRing((0,0,0))
        time.sleep(0.1)
        
    except OSError as error:
        print(error)
        continue

        




