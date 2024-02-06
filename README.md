# MakerspaceNetwork
In-house method for communitcation between computers and Raspberry Pi PicoW's.  

## For Desktop: mint/server.py
Python server for desktop (tested with Linux Mint)
* To INSTALL: copy ```server.py``` and ```index.html``` files to their own directory.
* serves ```index.html``` (GET at "/")
To run use:
```
python3 server.py
```


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

# Example Usage PicoW

This example will 
* create a button on the web page 
* on a click, send a message to the server
* server recieves the message and does something (get the time, or light the led on the Pico)
* server sends a message back to the webpage (client) to let it know what happened.

## Create button (html) (index.html)
Inside the ```index.html``` file's ```<body>``` tags add button code:
```html
<input type="button" id = "ledON" value="LED ON">
```
Give it a unique ```id```, and the ```value``` is what shows up on the button.

## Send message on click (JavaScript) (index.html)
Inside the ```index.html``` file's ```<script>``` tags add code to detect a click on the button and send message to server:
```js
    ledON.addEventListener("click", function(){
        sendRequest("/", "lightON");
    })
```
The first argument ("/"), indicates the base of the webpage url (does not need to change), and the second argument is the ```action``` paramenter that's sent to the server (see the protocol). A third argument would be the ```value``` parameter.

The message is sent as a POST request.

## Server Recieve Message (code.py)
The server recieves the POST message sent to "/" in the ection that starts with:
```python
@server.route("/", "POST")
```

Data recieved with the right protocol (see above) will be accessible as:
```python
data['action']
data['value']
```

To turn the pico's onboard LED (assuming that the variable ```led``` is set up previously in the code) on we do:
```python
    if (data['action'] == "lightON"):
            led.value = True
            rData['item'] = "onboardLED"
            rData['status'] = led.value
```

Notice that we set the values of ```rData``` which is returned to the client (webpage) at the end of the function.

## Webpage handles the reply
The reply from the server gets caught in the ```sendRequest``` function in the ```//Handle responses``` sectioin. For the response for this example is captured and the "status" is put into the DIV with the id "ledStatus" on the webpage with:
```js
                //Handle responses
                if (data["item"] == "onboardLED") {
                    ledStatus.innerText = data["status"];
                }
```

## Test
* Open ```code.py``` in Thonny and run.
* Click on the url link in the Thonny Shell to get the webpage
* Click the "LED ON" and "LED OFF" buttons on the page. 
    * The led on the picoW should turn on and off, and it should say "true" and "false" on the webpage.