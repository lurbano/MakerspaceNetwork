# Goes with programming lessons on: https://soriki.com/pico/
# Lensyl Urbano

import board
import neopixel

# Settings
nPix = 1               # number of led's in the strip
ledPin = board.GP28     # Pin on the RPi Pico (most likely GP0, GP15, or GP27)

pixels = neopixel.NeoPixel(ledPin, nPix)

pixels[0] = (20,20,0)
#pixels[-1] = (0,20,0)
