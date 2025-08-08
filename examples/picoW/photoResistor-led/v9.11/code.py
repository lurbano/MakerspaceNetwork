'''
Runs PicoW with a photoresistor and LED (neopixel) attached

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

'''PHOTORESISTOR SETUP'''
from photoResist import *
pr = photoResist(board.A0, maxVal=30000, minVal=9000)  #GP26

'''LED SETUP'''
from ledPixelsPico import *
pix = ledPixels(1, board.GP15)


#  onboard LED setup
led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
led.value = False

from uNetComm import *
deviceInfo = {
    'deviceName': 'photoResistor',
    'notes': 'picoW measuring light levels in the Makerspace',
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

    # Measure light level
    if (data['action']) == 'photoResistor':
        rData['item'] = "photoResistor"
        rData['status'] = pr.getPercent()

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

@server.route("/photoResistor", "GET")
def ledButton(request: HTTPRequest):
    rData = {}

    rData['item'] = "photoResistor"
    rData['status'] = pr.getPercent()

    with HTTPResponse(request) as response:
        response.send(json.dumps(rData))



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
ping_address = ipaddress.ip_address("8.8.4.4")

# log device on makerspace network
try:
    regInfo = {"ip": f'{wifi.radio.ipv4_address}:{port}',
               "deviceName": deviceInfo['deviceName'],
               "hostname": deviceInfo['hostname'],
               "notes": deviceInfo['notes']
               }
    regData = comm.request("http://makerspace.local:27182", "registerDevice", regInfo)
    print('registered:', regData.text)
except:
    #go to local mode
    print("Failed to register to Makerspace Network")

clock = time.monotonic() #  time.monotonic() holder for

while True:
    try:
        #  set led light level inversely related to light level
        pix.light(0, (250*pr.getPercent()/100, 0, 0))
        server.poll()
    # pylint: disable=broad-except
    except Exception as e:
        print(e)
        continue



