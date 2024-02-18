# MakerspaceNetwork
In-house method for communitcation between computers and Raspberry Pi PicoW's.  

## For Desktop: mint/server.py
Python server for desktop (tested with Linux Mint). Uses aoihttp to be asynchronous, so we can do other things while still serving.
* To INSTALL: copy ```server.py```, ```index.html```, and ```uAio.py``` files to your serving directory.
* Currently the program will attempt to get the ip address for hosting using ```hostname``` which has been tested on linux mint. Otherwise it will revert to "localhost"
* serves ```index.html``` (GET at "/")
To run use:
```bash
python3 server.py
```
May have to install aiohttp with:
```bash
pip3 install aiohttp
```

![Network Diagram](MakerspaceNetwork-diagram.svg)

## For PicoW: picoW/code.py
PicoW server using adafruit's requests
* To INSTALL: Download and copy the circuitpython uf2 to the Pico from:
    * https://circuitpython.org/board/raspberry_pi_pico_w/
* COPY: all files and folders in the ```picoW``` folder to the Pico. The```code.py``` file should run automatically on the Pico, but use Thonny (recommended) to debug.


## Makerspace POST protocol:
This simple protocol, in JSON format, facilitate sending data between picos and the main server.

e.g.
```json
{
    'action': "getTime", 
    'value': ""
}
```

* the servers handle POST data in JSON in the form (where "lightON" is an example value).  'action' is a single string for quick messages/instructions. "value" can be any string, you just have to write the code to handle it.


* the server returns the 'rData' dictionary to pass info back to the calling computer with:
    * rData['item']
    * rData['status']

(Note: on the webpage (client) the returned data is processed and renamed "data")

