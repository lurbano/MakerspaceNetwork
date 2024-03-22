
import board
import neopixel

nPix = 128
pixels = neopixel.NeoPixel(board.GP15, nPix)

for i in range(nPix):
    pixels[i] = (0,0,100)
pixels[1] = (200,0,0)
pixels.show()
print("done")