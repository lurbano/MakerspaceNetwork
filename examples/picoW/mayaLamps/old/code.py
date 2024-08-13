# SPDX-FileCopyrightText: 2022 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

#import secrets  # pylint: disable=no-name-in-module

import socketpool
import wifi

from adafruit_httpserver.mime_type import MIMEType
from adafruit_httpserver.request import HTTPRequest
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.server import HTTPServer

import neopixel
import touchio
import json
import board
from digitalio import DigitalInOut, Direction
import time
from ledPixelsPico import *

nPix = 32
pix = ledPixels(nPix, board.GP15)
ledMode="rainbow"

with open("index.html") as f:
    webpage = f.read()


#ssid, password = secrets.WIFI_SSID, secrets.WIFI_PASSWORD  # pylint: disable=no-member
ssid, password = "TFS Students", "Fultoneagles"  # pylint: disable=no-member

print("Connecting to", ssid)
wifi.radio.connect(ssid, password)
print("Connected to", ssid)

pool = socketpool.SocketPool(wifi.radio)
server = HTTPServer(pool)


def requestToArray(request):
    raw_text = request.body.decode("utf8")
    print("Raw")
    data = json.loads(raw_text)
    return data

@server.route("/")
def base(request: HTTPRequest):
    """
    Serve the default index.html file.
    """
    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
        #response.send(f"{webpage()}")
        response.send(webpage)


led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
led.value = False
@server.route("/led", "POST")
def ledButton(request: HTTPRequest):
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
        
    with HTTPResponse(request) as response:
        response.send(json.dumps(rData)) 
     
print(f"Listening on http://{wifi.radio.ipv4_address}:80")
# Start the server.
server.start(str(wifi.radio.ipv4_address))

touch = touchio.TouchIn(board.GP16)
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
            for j in range(255):
                for i in range(pix.nPix):
                    pixel_index = (i * 256 // pix.nPix) + j
                    pix.pixels[i] = pix.wheel(pixel_index & 255, 0.5)

                pix.pixels.show()

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

        
