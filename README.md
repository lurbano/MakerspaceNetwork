# MakerspaceNetwork


## Desktop: mint/server.py
Python server for desktop (tested with Linux Mint)
* serves (GET at "/"): ```index.html```
To run use:
```
python3 server.py
```


## PicoW: picoW/code.py
PicoW server using adafruit's requests
* install: Download and copy the circuitpython uf2 to the Pico from:
    * https://circuitpython.org/board/raspberry_pi_pico_w/
* copy: all files and folders in the ```picoW``` folder to the Pico. The```code.py``` file should run automatically on the Pico, but use Thonny (recommended) to debug.


## Makerspace POST protocol:
* handles POST data in JSON in the form (where "lightON" is an example value).  'action' is a single string for quick messages/instructions. "value" can be any string, you just have to write the code to handle it.
    * {'action': "getTime", 'value': ""}
* POST returns the 'rData' dictionary to pass info back to the calling computer with:
    * rData['item']
    * rData['status']

# Example Usage

This example will 
* create a button on the web page 
* on a click, send a message to the server
* server recieves the message and does something (get the time, or light the led on the Pico)
* server sends a message back to the webpage (client) to let it know what happened.

## Create button (html)
Inside the ```index.html``` file's ```<body>``` tags add button code:
```
<input type="button" id = "ledON" value="LED ON">
```
Give it a unique ```id```, and the ```value``` is what shows up on the button.

## Send message on click (JavaScript)
Inside the ```index.html``` file's ```<script>``` tags add code to detect a click on the button and send message to server:
```
    ledON.addEventListener("click", function(){
        sendRequest("/", "lightON");
    })
```
The first argument ("/"), indicates the base of the webpage url (does not need to change), and the second argument is the ```action``` paramenter that's sent to the server (see the protocol). A third argument would be the ```value``` parameter.