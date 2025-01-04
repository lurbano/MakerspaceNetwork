import board
import neopixel
from ledPixelsPico import *

nPix = 61*2
pix = ledPixels(nPix, board.GP27)

wait = 0.01
ranges = [range( 0, 7),
          range(13,28),
          range(33,48),
          range(53,61),
          range(64,79),
          range(84,99),
          range(104,119)
         ]

nRng = len(ranges)
pix.clear()





# Maya's lamps picoW

import socketpool
import wifi

import touchio
import json
from digitalio import DigitalInOut, Direction
import time
from ledPixelsPico import *

from adafruit_httpserver import Server, Request, Response, POST


ledMode="rainbow"

from uNetComm import *
deviceInfo = {
    'deviceName': 'MPU: Artwork',
    'notes': 'Art Piece by Maren',
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

@server.route("/")
def base(request: Request):
    """
    Serve the default index.html file.
    """
    return Response(request, f"{webpage}", content_type='text/html')


led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
led.value = False
@server.route("/led", "POST")
def ledButton(request: Request):
    # raw_text = request.body.decode("utf8")
    global ledMode
    print("Raw")
    # data = json.loads(raw_text)
    data = requestToArray(request)
    print(f"data: {data} & action: {data['action']}")
    rData = {}
    
    if (data['action'] == 'ON'):
        led.value = True
        ledMode="rainbow"
        
    if (data['action'] == 'OFF'):
        led.value = False
        ledMode="OFF"
    
    rData['item'] = "led"
    rData['status'] = data['action']
    
    print("ledMode:", ledMode)
        
    return Response(request, json.dumps(rData)) 
     
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



touch = touchio.TouchIn(board.GP26)
print("Start touch", touch.value)
def touchCheck():
    if touch.value:
        pix.light(0, (200,0,0))
        while touch.value:
            time.sleep(0.1)
        return True
    else:
        return False

while True:
    try:
        # Do something useful in this section,
        # for example read a sensor and capture an average,
        # or a running total of the last 10 samples
        if ledMode == "rainbow":
            # rainbow
            for t in range(255):
                for r in range(nRng):
                    pixel_index = (r*256 // nRng) + t
                    #print(r, ranges)
                    col = pix.wheel(pixel_index & 255, 0.5)
                    pix.setColorInRange(col, ranges[r])
                    time.sleep(wait)

                #pix.pixels.show()

                # check for anything from the webpage
                server.poll()
                if ledMode == "rainbow":
                    time.sleep(0.01)
                else:
                    break

                # check for a touch signal
                if touchCheck():
                    ledMode = "OFF"
                    break

        elif ledMode == "OFF":
            pix.off()

            if touchCheck():
                ledMode = "rainbow"
                
        else:
            pix.off()

        # Process any waiting requests
        server.poll()
    except OSError as error:
        print(error)
        continue

        













# while True:
#     for t in range(255):
#         for r in range(nRng):
#             pixel_index = (r*256 // nRng) + t
#             #print(r, ranges)
#             col = pix.wheel(pixel_index & 255, 0.5)
#             pix.setColorInRange(col, ranges[r])
#             time.sleep(wait)


