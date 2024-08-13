

# Example Usage Desktop Server

This example shows the procedure to add a button to the served webpage that gets the current date and time from the server.
* create a button on the web page 
* on a click, send a message to the server
* server recieves the message and does something (get the time)
* server sends a message back to the webpage (client) to let it know what happened.
* the some of the returned information gets put on the webpage

## Create button (html) (index.html)
Inside the ```index.html``` file's ```<body>``` tags add code for a button and a DIV to put the returned information:
```html
<input type="button" id = "timeBut" value="Get Time">
    <div id="timeSlot">Time</div>
```
Give each thing a unique ```id``` ("timeBut" in this case). The ```value```  of the button shows up on the button. The text between the div tags ("Time") shows up on the webpage as a default.

## Send message on click (JavaScript) (index.html)
Inside the ```index.html``` file's ```<script>``` tags add code to detect a click on the button and send message to server:
```js
    timeBut.addEventListener("click", function(){
        sendRequest("/", "getTime");
    })
```
The first argument ("/"), indicates the base of the webpage url (does not need to change), and the second argument is the ```action``` paramenter that's sent to the server (see the protocol). A third argument would be the ```value``` parameter.

The message is sent as a POST request.

## Server Recieve Message (code.py)
The server recieves the POST message sent to "/" and sends it to the ```handlePost``` function:
```python
async def handlePost(request):
```

Data recieved with the right style/protocol (see the main README.md file) will be accessible as:
```python
data['action']
data['value']
```

In this case the data['action'] is "getTime", so we create an if statement to deal with any messages who's action is "getTime".
```python
    if data['action'] == "getTime":
        now = datetime.now()

        print(now.ctime())
        rData['item'] = "time"
        rData['status'] = now.ctime() # a string representing the current time
```

Notice that we set the values of ```rData``` which are returned to the client (webpage) at the end of the function.

## Webpage handles the reply
The reply from the server gets caught by the ```sendRequest``` function on the webpage, in the ```//Handle responses``` section. The response is captured and put into the ```data``` dictionary (which is the ```rData``` dictionary that was returned from the server, renamed as 'data["item"]' and 'data["status"]'). In this example, the "status" is put into the DIV with the id "timeSlot" on the webpage with:
```js
                //Handle responses
                if (data["item"] == "time") {
                    console.log("Got the time: ", data["status"]);
                    timeSlot.innerText = data["status"];
                }
```


## Test
* Run:
```bash
python3 server.py
```
* Click on the url link in the Thonny Shell to get the webpage
* Click the "Get Time" button


