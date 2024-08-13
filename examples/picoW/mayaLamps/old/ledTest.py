import board
import neopixel
from ledPixelsPico import *

nPix = 64

pix = ledPixels(nPix, board.GP15)

pix.brightness = 0.5

pix.rainbow()
