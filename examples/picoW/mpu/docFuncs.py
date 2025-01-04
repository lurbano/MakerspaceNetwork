import board
import neopixel
import time

pixels = neopixel.NeoPixel(board.GP0, 20)

def lightsOff():
    for i in range(20):
        pixels[i] = (0,0,0)

def lightUp(n=20, color=(0,0,10)):
    for i in range(n):
        pixels[i] = color
        time.sleep(0.1)

def lastLights(n=20, color=(0,10,0)):
    startLed = 20-n
    for i in range(startLed, 20):
      print(i)
      pixels[i] = color
      time.sleep(0.1)

def complementaryColor(color):
    r = 255 - color[0]
    g = 255 - color[1]
    b = 255 - color[2]
    return (r, g, b)

def allRandom(dt=2, mag=10):
    while True:
        for i in range(20):
            r = int(mag * random())
            g = int(mag * random())
            b = int(mag * random())
            pixels[i] = (r, g, b)
        time.sleep(2.5)
