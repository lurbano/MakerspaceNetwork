
import socketpool
import wifi

from adafruit_httpserver import Server, Request, Response, POST

import json
import board
from digitalio import DigitalInOut, Direction
import time

from cHex import *
ts = tileset()
lightSwitch = "on"
lightSwitchOld = "off"

# SET UP NETWORK
from uNetComm import *
deviceInfo = {
    'deviceName': 'Icebreaker: Hexagons',
    'notes': 'Icebreaker project with individual hexagons for each community member. ',
    'hostname': ''
    }

#  connect to network
print()
print("Connecting to WiFi")
#  connect to your SSID
wifi.radio.connect('TFS Students', 'Fultoneagles')

with open("index.html") as f:
    webpage = f.read()

print("Connected to WiFi")
pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, "/static", debug=True)
port = 80
comm = uNetComm(pool)
#/ NETWORK 


#  onboard LED setup
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
def base(request: Request):
    """
    Serve the default index.html file.
    """
    return Response(request, f"{webpage}", content_type='text/html')


@server.route("/", "POST")
def base(request: Request):
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

    return Response(request, json.dumps(rData))

@server.route("/led", "GET")
def ledButton(request: HTTPRequest):
    rData = {}
    
    if led.value:
        led.value = False
    else:
        led.value = True
    
    rData['item'] = "onboardLED"
    rData['status'] = led.value
        
    return Response(request, json.dumps(rData))

 
# STARTING SERVER
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
#/ STARTING SERVER


while True:
    try:
        # Process any waiting requests
        server.poll()
        #print(lightSwitch)
        if (lightSwitch != lightSwitchOld):
            
            lightSwitchOld = lightSwitch
            
            if lightSwitch == 'on':
                ts.lightUp()
            elif lightSwitch == 'off':
                ts.lightOff()
        time.sleep(0.1)
        
    except OSError as error:
        print(error)
        continue

        



