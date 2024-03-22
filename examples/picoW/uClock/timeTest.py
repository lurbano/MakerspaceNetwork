import adafruit_ntp
import socketpool
import time
import wifi
from uSchedule import *

#ssid, password = secrets.WIFI_SSID, secrets.WIFI_PASSWORD  # pylint: disable=no-member
ssid, password = "TFS Students", "Fultoneagles"  # pylint: disable=no-member

print("Connecting to", ssid)
wifi.radio.connect(ssid, password)
print("Connected to", ssid)

pool = socketpool.SocketPool(wifi.radio)
ntp = adafruit_ntp.NTP(pool, tz_offset=-6)
t = ntp.datetime
print("Time:", t)

#daylight saving time
if (t.tm_mon <= 2 or t.tm_mon == 12):
    t_hour = t.tm_hour 
elif (t.tm_mon == 3 and t.tm_mday < 10):
    t_hour = t.tm_hour 
elif (t.tm_mon == 11 and t.tm_mday > 3):
    t_hour = t.tm_hour 
else:
    t_hour = t.tm_hour + 1
    
print("Time:", t.tm_year)

lt = f'{t_hour}:{t.tm_min}:{t.tm_sec}'

ut = uTime(lt)
print(ut)
