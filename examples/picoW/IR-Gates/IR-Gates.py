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
#from digitalio import DigitalInOut, Direction
import digitalio
import neopixel
from adafruit_httpserver import Server, Request, Response, POST


class IR:
    def __init__(self, IR_GP = board.GP28, LED_GP = board.GP22, startTime=time.monotonic()):
        self.break_beam = digitalio.DigitalInOut(IR_GP)
        self.break_beam.direction = digitalio.Direction.INPUT
        self.break_beam.pull = digitalio.Pull.UP
        
        self.pixels = neopixel.NeoPixel(LED_GP, 1)
        self.pixels[0] = (200,0,0)
        
        time.sleep(0.5)
        print(self.break_beam.value)
        if self.break_beam.value:
            self.pixels[0] = (0,200,0)
            
        self.startTime = startTime
        self.startFlag = False
        self.senseStart = -1.0
        self.senseEnd = -1.0
        self.senseDuration = -1.0
        
    def monitorLED(self):
        if self.break_beam.value:
            self.pixels[0] = (0,200,0)
        else:
            self.pixels[0] = (200,0,0)
            
    def monitor(self):
        self.monitorLED()
        if (not self.startFlag) and (not self.break_beam.value):
            self.senseStart = time.monotonic()
            self.startFlag = True
        if (self.startFlag) and (self.break_beam.value):
            self.senseDuration = time.monotonic() - self.senseStart
            self.startFlag = False
            return True
        return False
        
        
startTime = time.monotonic()
l_monitor = False  # default monitoring set to off
gateTimes = []

gates = []
gates.append( IR(IR_GP = board.GP28, LED_GP = board.GP22, startTime = startTime) )
gates.append( IR(IR_GP = board.GP16, LED_GP = board.GP17, startTime = startTime) )
gates.append( IR(IR_GP = board.GP14, LED_GP = board.GP15, startTime = startTime) )
gates.append( IR(IR_GP = board.GP2, LED_GP = board.GP8, startTime = startTime) )

print('done gate setup')




#  onboard LED setup
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led.value = False

from uNetComm import *
deviceInfo = {
    'deviceName': 'IR-Gate-Ramp',
    'notes': 'Ramp of IR gates.',
    'hostname': ''
    }

#  connect to network
print()
print("Connecting to WiFi")
#  connect to your SSID
wifi.radio.connect('TFS Students', 'Fultoneagles')

# get web page
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

#     if (data['action'] == "Forward"):
#         robotWheels.forward(1)
#         
#         rData['item'] = "Forward"
#         rData['status'] = 1

    
    if (data['action'] == "startMonitoring"):

        global l_monitor
        
        l_monitor = True

        rData['item'] = "monitoring"
        rData['status'] = l_monitor

    if (data['action'] == "getData"):

        global l_monitor
        global gateTimes
        
        l_monitor = False

        rData['item'] = "GateData"
        rData['status'] = gateTimes


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
print("Gates: ", len(gates))

while True:
    try:
        server.poll()
        #print (l_monitor, l_monitoring)
        
        if (not l_monitor): # start monitoring
            print("Starting Monitoring")
            l_monitor = True
            for i in range(len(gates)):
                gates[i].startTime = time.monotonic()
            
            print("gateTimes:", gateTimes)
            gateTimes = []
            
        else:
            #print("gate check at:", len(gates), time.monotonic())
            for i in range(len(gates)):
                gate = gates[i]
                if gate.monitor():
                    data = {}
                    data["gate"] = i
                    data["time"] = gate.senseStart-startTime
                    data["duration"] = gate.senseDuration
                    print(data)
                    gateTimes.append(data)
                    

            
    except Exception as e:
        print(e)
        continue









