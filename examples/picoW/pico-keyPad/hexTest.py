"""CircuitPython Essentials Capacitive Touch example"""
import time
import board
import touchio
from ledPixelsPico import *


class hexFunc:
    def __init__(self, tGP = board.GP18, lGP = board.GP22,  color = [0,0,50]):
        self.tGP = tGP
        self.lGP = lGP
        self.ledPix = ledPixels(24, lGP)
        self.ledPix.clear()
        self.touch = touchio.TouchIn(tGP)
        self.color = color
        
    def Hexagon(self):
        if self.touch.value:
            self.ledPix.setColor(self.color)
        else:
            self.ledPix.clear()
            
hex = hexFunc(board.GP2, board.GP3)


while True:
    hex.Hexagon()