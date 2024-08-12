# SPDX-FileCopyrightText: 2023 Liz Clark for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import time
import ipaddress
import wifi
import socketpool
import board
import microcontroller
import json
from digitalio import DigitalInOut, Direction
from adafruit_httpserver import Server, Request, Response, POST


#  onboard LED setup
led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
led.value = False

from uNetComm import *

#  connect to network
print()
print("Connecting to WiFi")

#  set static IP address
# ipv4 =  ipaddress.IPv4Address("192.168.1.42")
# netmask =  ipaddress.IPv4Address("255.255.255.0")
# gateway =  ipaddress.IPv4Address("192.168.1.1")
# wifi.radio.set_ipv4_address(ipv4=ipv4,netmask=netmask,gateway=gateway)
#  connect to your SSID
wifi.radio.connect('Wifipower', 'defacto1')

print("Connected to WiFi")
pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, "/static", debug=True)
port = 80
comm = uNetComm(pool)

with open("index.html") as f:
    webpage = f.read()

# UTILITY FUNCTIONS
def requestToArray(request):
    raw_text = request.body.decode("utf8")
    print("Raw")
    data = json.loads(raw_text)
    return data


# ROUTES
#  route default static IP
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

    if (data['action']) == 'photoResistor':
        prData = comm.request("http://20.1.0.96", "photoResistor", "")
        rData = json.loads(prData.text)

    return Response(request, json.dumps(rData))
    # with Response(request) as response:
    #     response.send(json.dumps(rData))

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
    
# @server.route("/photoResistor", "GET")
# def ledButton(request: Request):
#     rData = {}
#     
#     rData['item'] = "photoResistor"
#     rData['status'] = pr.getPercent()
#     
#     return Response(request, json.dumps(rData))
    
# #  if a button is pressed on the site
# @server.route("/", POST)
# def buttonpress(request: Request):
#     #  get the raw text
#     raw_text = request.raw_request.decode("utf8")
#     print(raw_text)
#     #  if the led on button was pressed
#     if "ON" in raw_text:
#         #  turn on the onboard LED
#         led.value = True
#     #  if the led off button was pressed
#     if "OFF" in raw_text:
#         #  turn the onboard LED off
#         led.value = False
#     #  reload site
#     return Response(request, f"{webpage()}", content_type='text/html')

print("starting server..")
# startup the server
try:
    server.start(str(wifi.radio.ipv4_address), port)
    print("Listening on http://%s:80" % wifi.radio.ipv4_address)
    print(f"Listening on http://{wifi.radio.ipv4_address}:{port}" )
#  if the server fails to begin, restart the pico w
except OSError:
    time.sleep(5)
    print("restarting..")
    microcontroller.reset()
ping_address = ipaddress.ip_address("8.8.4.4")

clock = time.monotonic() #  time.monotonic() holder for 

while True:
    try:
        #  every 30 seconds, ping server & update temp reading
        if (clock + 30) < time.monotonic():
            if wifi.radio.ping(ping_address) is None:
                
                print("lost connection")
            else:
                
                print("connected")
            clock = time.monotonic()
            

        
        server.poll()
    # pylint: disable=broad-except
    except Exception as e:
        print(e)
        continue



