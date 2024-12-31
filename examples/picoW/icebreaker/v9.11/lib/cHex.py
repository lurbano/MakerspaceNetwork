import board 
import time
import neopixel
npix = 38 

pixels = neopixel.NeoPixel(board.GP27, npix)
class hex:
    def __init__(self,n): #n is the number of the first 2 pixels for this hex.
        self.i=n
        self.j=n+1
    def top(self,color=(255,255,255)):
        pixels[self.i]=color
        print(color)
    def bot(self,color=(255,255,255)):
        pixels[self.j]=color
    def color(self,color=(255,255,255)):
        pixels[self.i]=color
        pixels[self.j]=color
#hexes = []
#for i in range(19):
#    hexes.append(hex(i*2))

class tileset:
    def __init__(self):
        self.hexes = []
        for i in range(19):
            self.hexes.append(hex(i*2))
    def makeRed(self,dt=.5):
        for h in self.hexes:
            h.color((255,0,0))
            time.sleep(dt)
    def makeColor(self,cl=(0,255,0),dt=.1):
        for h in self.hexes:
            h.color(cl)
            time.sleep(dt)
    def firstCircle(self,col=(255,0,0)):
        self.hexes[0].color(col)
    def secondRing(self,col=(255,255,255)):
        for i in range(1,7):
            self.hexes[i].color(col)
    def lastRing(self,col=(0,0,255)):
        for i in range(7,19):
            self.hexes[i].color(col)
    def off(self,cl=(0,0,0)):
        for h in self.hexes:
            h.color(cl)
    def repeat(self,n=10,dt=.25):
        for i in range(n):
            self.firstCircle()
            time.sleep(dt)
            self.secondRing()
            time.sleep(dt)
            self.lastRing()
            time.sleep(dt)
            self.off()
    def infinite(self,dt=.25):
        while True:
            self.repeat(n=1,dt=dt)
            
    def lightUp(self, dt = 0.5):
        self.firstCircle((0,0,200))
        time.sleep(dt)
        self.secondRing((0,200,0))
        time.sleep(dt)
        self.lastRing((200,0,0))
        time.sleep(dt)
        
    def lightOff(self, dt=0.5):
        self.lastRing((0,0,0))
        time.sleep(dt)
        self.secondRing((0,0,0))
        time.sleep(dt)
        
        self.firstCircle((0,0,0))
        time.sleep(dt)
