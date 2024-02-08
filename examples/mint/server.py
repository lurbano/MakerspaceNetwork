import asyncio
from aiohttp import web, ClientSession
from datetime import datetime
import json
from getIP import getIP

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
    
    response = json.dumps(rData)
    print("Response: ", response)
    # return web.json_response(response)
    return web.Response(text=response, content_type='text/html')

    
async def print_hello():
    while True:
        print("Hello")
        await asyncio.sleep(1)

async def getLightLevel(dt=1):
    while True:
        async with ClientSession() as session:
            async with session.get('http://20.1.0.96:80/photoResistor') as resp:
                print(resp.status)
                print(await resp.text())
        await asyncio.sleep(dt)

async def main():
    app = web.Application()
    app.router.add_get('/', handle)
    app.router.add_post("/", handlePost)

    runner = web.AppRunner(app)
    await runner.setup()
    try: 
        host = getIP()
    except:
        host = "localhost"
        print("Unable to find IP address. Reverting to localhost.")
    site = web.TCPSite(runner, host, 8080)  # Bind to the local IP address
    await site.start()
    print(f"Server running at http://{host}:8080/")

    asyncio.create_task(print_hello())
    asyncio.create_task(getLightLevel(dt=5))
    await asyncio.Event().wait()  # Keep the event loop running

if __name__ == '__main__':
    asyncio.run(main())
