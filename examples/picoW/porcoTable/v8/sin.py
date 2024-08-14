from ledPixelsPico import *
import time

ring = ledPixels(76, board.GP20)

#ring.threeSins(ncycles=1)
freq = 1
phase = 0
dp = 0.001

while True:
    phase += dp
    ring.sin(freq, phase)
    ring.show()
    time.sleep(0.1)