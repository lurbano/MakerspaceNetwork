import asyncio
from aiohttp import web, ClientSession
from datetime import datetime
import json
#from getIP import getIP
from uAio import *

# database
from baseStationDB import *
db = baseStationDB()

dir_path = os.path.dirname(os.path.abspath(__file__))
qr_path = f'{dir_path}/qrCodes/'

async def handle(request):
    with open(dir_path+"/"+"index.html", "r") as f:
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

    if data['action'] == 'photoResistor':
        # send request to the Makerspace picoW with the photoresistor
        info = await postRequest("20.1.0.96:80", action="photoResistor", value="")
        print("Requested from pr Pico: ", info)
        rData = json.loads(info)

    if data['action'] == 'registerDevice':
        # register device with the base station
        info = data['value']
        print("Registering: ", info)
        db.updateLog(ip=info['ip'], 
               deviceName=info['deviceName'], 
               hostname=info['hostname'], 
               notes=info['notes'] )
        rData['item'] = 'registerDevice'
        rData['status'] = 'registered'

    if data['action'] == 'getDeviceTable':
        devices = db.activeDB.all()
        rData['item'] = 'getDeviceTable'
        rData['status'] = devices
    
    response = json.dumps(rData)
    print("Response: ", response)
    return web.Response(text=response, content_type='text/html')

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


async def main():
    app = web.Application()
    app.router.add_get('/', handle)
    app.router.add_post("/", handlePost)
    # path to qr codes
    app.router.add_routes([web.static('/qrCodes', qr_path)])

    runner = web.AppRunner(app)
    await runner.setup()
    port = 27182

    host = getIP()
    site = web.TCPSite(runner, host, port)  # Bind to the local IP address
    await site.start()
    print(f"Server running at http://{host}:{port}/")

    # asyncio.create_task(print_hello())
    # asyncio.create_task(getLightLevel(dt=5))

    '''Testing post request'''
    # await postRequest("192.168.1.142:8000", action="Rhythmbox", value="play")
    # await postRequest("192.168.1.142:8000", action="Rhythmbox", value="play")

    await asyncio.Event().wait()  # Keep the event loop running

if __name__ == '__main__':
    asyncio.run(main())
