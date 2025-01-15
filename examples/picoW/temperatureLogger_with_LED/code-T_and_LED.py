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
import neopixel

from uDS18x20 import *


# temperature sensor setup
thermo = uDS18X20(board.GP5)
T = thermo.read()
print(f"Temperature = {T}")

# timer
startTime = time.monotonic()

#  onboard LED setup
led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
led.value = False

# status LED setup
ledPin = board.GP28     # Pin on the RPi Pico (most likely GP0, GP15, or GP27)
pixels = neopixel.NeoPixel(ledPin, 1) # 1 for single LED
pixels[0] = (20,0,20)

# SET UP NETWORK
from uNetComm import *
deviceInfo = {
    'deviceName': 'Temperature Logger 2 (with LED)',
    'notes': 'picoW with a temperature sensor (deg. C) and a LED to indicate status',
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
        pixels[0] = (0,0,20)  # indicate reading temperature
        T = thermo.read()
        time.sleep(0.5)
        pixels[0] = (0,20,0) # indicate device is ready
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
    
    pixels[0] = (0,20,0)
        

#  if the server fails to begin, restart the pico w
except OSError:
    pixels[0] = (20,0,0)
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


