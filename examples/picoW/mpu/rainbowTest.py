import board
import neopixel
from ledPixelsPico import *

nPix = 61*2
pix = ledPixels(nPix, board.GP0)

wait = 0.01
ranges = [range( 0, 7),
          range(13,28),
          range(33,48),
          range(53,61),
          range(64,79),
          range(84,99),
          range(104,119)
         ]

nRng = len(ranges)
pix.clear()

while True:
    for t in range(255):
        for r in range(nRng):
            pixel_index = (r*256 // nRng) + t
            #print(r, ranges)
            col = pix.wheel(pixel_index & 255, 0.5)
            pix.setColorInRange(col, ranges[r])
            time.sleep(wait)

