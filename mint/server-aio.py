import asyncio
from aiohttp import web
from datetime import datetime
import json

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

async def main():
    app = web.Application()
    app.router.add_get('/', handle)
    app.router.add_post("/", handlePost)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    asyncio.create_task(print_hello())
    await asyncio.Event().wait()  # Keep the event loop running

if __name__ == '__main__':
    asyncio.run(main())