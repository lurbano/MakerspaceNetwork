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

from uDS18x20 import *


# temperature sensor setup
thermo = uDS18X20(board.GP21)
T = thermo.read()
print(f"Temperature = {T}")

# timer
startTime = time.monotonic()

#  onboard LED setup
led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
led.value = False

# SET UP NETWORK
from uNetComm import *
deviceInfo = {
    'deviceName': 'Temperature Logger 1',
    'notes': 'picoW with a temperature sensor (deg. C)',
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

    # Temperature
    if (data['action']) == 'temperature':
        T = thermo.read()
        rData['item'] = "T"
        rData['status'] = T

    # time and Temperature
    if (data['action']) == 'timeTemperature':
        global startTime
        T = thermo.read()
        t = time.monotonic() - startTime
        rData['item'] = "timeTemperature"
        rData['status'] = {"t": t, "T": T}

    # reset timer
    if (data['action']) == 'resetTimer':
        # global startTime
        T = thermo.read()
        startTime = time.monotonic()
        
        rData['item'] = "timeTemperature"
        rData['status'] = {"t": 0, "T": T}

    

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
   
        server.poll()
    # pylint: disable=broad-except
    except Exception as e:
        print(e)
        continue



