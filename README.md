# MakerspaceNetwork


## Desktop: mint/server.py
Python server for desktop (tested with Linux Mint)
* serves (GET at "/"): ```index.html```

## PicoW: picoW/code.py
PicoW server using adafruit's requests

## Makerspace POST protocol:
* handles POST data in JSON in the form (where "lightON" is an example value).  'action' is a single string for quick messages/instructions. "value" can be any string, you just have to write the code to handle it.
    * {'actoin': "getTime", 'value': ""}
* POST returns the 'rData' dictionary to pass info back to the calling computer with:
    * rData['item']
    * rData['status']



