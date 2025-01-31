import asyncio
from aiohttp import web, ClientSession
from datetime import datetime
import json
#from getIP import getIP
from uAio import *
import os

homedir="/home/lurbano/MkMac"

deviceInfo = {
    'deviceName': 'Makerspace iMac',
    'notes': 'iMac in the Makersapce ',
    'hostname': ''
    }


async def handle(request):
    with open("index.html", "r") as f:
        html_content = f.read()
    return web.Response(text=html_content, content_type='text/html')

async def handlePost(request):
    data = await request.json()
    rData = {}
    print(data)
    # print(data["action"], data["value"])

    if data['action'] == "getTime":
        now = datetime.now()
        print(now.ctime())
        rData['item'] = "time"
        rData['status'] = now.ctime() # a string representing the current time

    if data['action'] == "startEngine":
        #os.system(f"mplayer {homedir}/audio/powerup.wav")
        asyncio.create_task( play_sound("powerup.wav"))
        rData['item'] = "powerUp"
        rData['status'] = "play"

    if data['action'] == "playSound":
        soundfile = data["value"]
        #os.system(f"mplayer {homedir}/audio/powerup.wav")
        asyncio.create_task( play_sound(soundfile))
        rData['item'] = "playSound"
        rData['status'] = "play"


    if data['action'] == 'photoResistor':
        # send request to the Makerspace picoW with the photoresistor
        info = await postRequest("20.1.0.96:80", action="photoResistor", value="")
        print("Requested from pr Pico: ", info)
        rData = json.loads(info)
    
    response = json.dumps(rData)
    print("Response: ", response)
    return web.Response(text=response, content_type='text/html')

async def play_sound(soundfile="powerup.wav"):
    os.system(f"mplayer {homedir}/audio/{soundfile}")
        

# print "Hello" every 1 second (testing async)
async def print_hello():
    while True:
        print("Hello")
        await asyncio.sleep(1)

''' Get the light level from the MakerspaceNetwork Testing Pico'''
async def getLightLevel(dt=1):
    while True:
        await getRequest('20.1.0.96:80/photoResistor')
        # async with ClientSession() as session:
        #     async with session.get('http://20.1.0.96:80/photoResistor') as resp:
        #         print(resp.status)
        #         print(await resp.text())
        await asyncio.sleep(dt)

async def registerWithMakerspaceNetwork(host, port):
    
    regInfo = {"ip": f'{host}:{port}',
               "deviceName": deviceInfo['deviceName'],
               "hostname": deviceInfo['hostname'],
               "notes": deviceInfo['notes']
               }
    print(f"Registering device: ", regInfo)
    await postRequest("makerspace.local:27182", action="registerDevice", value=regInfo)


async def main():
    app = web.Application()
    app.router.add_get('/', handle)
    app.router.add_post("/", handlePost)

    runner = web.AppRunner(app)
    await runner.setup()

    host = getIP()
    port = 8080
    site = web.TCPSite(runner, host, 8080)  # Bind to the local IP address
    await site.start()
    print(f"Server running at http://{host}:8080/")

    # asyncio.create_task(print_hello())

    asyncio.create_task(registerWithMakerspaceNetwork(host, port))
    # asyncio.create_task(getLightLevel(dt=5))

    '''Testing post request'''
    # await postRequest("192.168.1.142:8000", action="Rhythmbox", value="play")
    # await postRequest("192.168.1.142:8000", action="Rhythmbox", value="play")

    await asyncio.Event().wait()  # Keep the event loop running

if __name__ == '__main__':
    asyncio.run(main())
