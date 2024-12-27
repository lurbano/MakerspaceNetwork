# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CircuitPython Essentials Capacitive Touch example"""
import time
import board
import touchio
from ledPixelsPico import *




class hexFunc(object):
    def __init__(self, tGP = board.GP18, lGP = board.GP22,  color = [0,0,250], id=-1):
        self.tGP = tGP
        self.lGP = lGP
        self.ledPix = ledPixels(24, lGP)
        self.ledPix.clear()
        self.touch = touchio.TouchIn(tGP)
        self.color = color
        self.id = id
        self.beingTouched = False
        
    def Hexagon(self):
        if self.touch.value:
            self.ledPix.setColor(self.color)
        else:
            self.ledPix.clear()
            
    def touching(self):
        value = self.touch.value
        #if value:
            #print("touching", self.id)
        return value
            
    def light(self):
        self.ledPix.setColor(self.color)            
        
    def off(self):
        self.ledPix.clear()
        
    def touchStart(self):
        self.beingTouched = True
        self.wasTouched = True
        self.touchStartTime = time.monotonic()
        self.light()
        print(f'start: {self.id}')
        
    def touchStop(self):
        self.beingTouched = False
        self.wasTouched = True
        self.touchStopTime = time.monotonic()
        self.off()
        print(f'stop: {self.id}, for: {self.touchStopTime-self.touchStartTime}')
        
    
    

class hexController:
    def __init__(self):
        
        self.hexes = []
        self.hexes.append(
            hexFunc(tGP=board.GP2, lGP=board.GP3, color=[250,0,0], id=len(self.hexes)))
        self.hexes.append(hexFunc(tGP=board.GP10, lGP=board.GP11, id=len(self.hexes)))
        self.hexes.append(hexFunc(tGP=board.GP12, lGP=board.GP13, id=len(self.hexes)))
        self.hexes.append(hexFunc(tGP=board.GP16, lGP=board.GP17, id=len(self.hexes)))
        self.hexes.append(hexFunc(tGP=board.GP18, lGP=board.GP19, id=len(self.hexes)))
        self.hexes.append(hexFunc(tGP=board.GP20, lGP=board.GP21, id=len(self.hexes)))
        self.hexes.append(hexFunc(tGP=board.GP14, lGP=board.GP15, id=len(self.hexes)))
        
        self.hexes[-1].hexes = self.hexes
        self.resetID = len(self.hexes)-1
        print("RESET ID: ", self.resetID)
        
        self.keySeq = []
        
    def lightAll(self):
        for hex in self.hexes:
            hex.light()
            
    def offAll(self):
        for hex in self.hexes:
            hex.off()
        
    def lightOnTouch(self):
        
        while True:
            for hex in self.hexes:
                if hex.touching():
                    hex.light()
                else:
                    hex.off()
                    
    def keyPad(self):
        
        
        while True:
            for hex in self.hexes:
                if hex.touching():
                    if hex.beingTouched == False:
                        hex.touchStart()
                        if hex.id == self.resetID:
                            self.lightAll()
                else:
                    if hex.beingTouched:
                        hex.touchStop()
                        self.keySeq.append(hex.id)
                        
                        if hex.id == self.resetID:
                            self.offAll()
                            print("Key Seq:", self.keySeq)
                            self.keySeq = []
                        
#                 if self.hexes[self.resetID].beingTouched:
#                     for h in self.hexes:
#                      h.light()
                        
#             if (self.hexes[self.resetID].touching()):
#                 for hex in self.hexes:
#                     hex.light()
                        

startTime = time.monotonic()
print("StartTime:", startTime)

hCon = hexController()

#hCon.lightOnTouch()
hCon.keyPad()




