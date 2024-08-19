'''
Basic PicoW networking setup

'''


import time
import ipaddress
import wifi
import socketpool
import board
import microcontroller
import json
from digitalio import DigitalInOut, Direction
from adafruit_httpserver import Server, Request, Response, POST

from numberLine import *

numLine = numberLine(ledPin = board.GP27, nPix=60, zeroLed=0, reverse=True)
#numLine.lightup(0, (10,0,0))
#numLine.lightup(3, (0,10,0))
#numLine.lightOdds()
numLine.options('lightZero')


#  onboard LED setup
led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
led.value = False

# SET UP NETWORK
from uNetComm import *
deviceInfo = {
    'deviceName': 'Light Bar 60',
    'notes': "Peter's clock light bar commandeered to be a number line.",
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
#/ NETWORK 

# UTILITY FUNCTIONS
def requestToArray(request):
    raw_text = request.body.decode("utf8")
    print("Raw")
    data = json.loads(raw_text)
    return data


# ROUTES
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

    # Test sending a request to another device
    if (data['action']) == 'numberPattern':
        opt = data['value']
        result = numLine.options(opt)
        
        rData['item'] = "numberPattern"
        rData['status'] = {"pattern": opt, "result": result}

    return Response(request, json.dumps(rData))


@server.route("/led", "GET")
def ledButton(request: Request):
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
    comm.registerWithBaseStation(regInfo)
    # regData = comm.request("http://makerspace.local:27182", "registerDevice", regInfo)
    # print('registered:', regData.text)
        

#  if the server fails to begin, restart the pico w
except OSError:
    time.sleep(5)
    print("restarting..")
    microcontroller.reset()
#/ STARTING SERVER

clock = time.monotonic() #  time.monotonic() holder for 

while True:
    try:
        #  every 30 seconds, ping server & update temp reading
          

        
        server.poll()
        time.sleep(0.1)
    # pylint: disable=broad-except
    except Exception as e:
        print(e)
        continue



