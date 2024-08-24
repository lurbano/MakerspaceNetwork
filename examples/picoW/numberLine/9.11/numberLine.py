import board
from ledPixelsPico import *

class numberLine(ledPixels):
    def __init__(self, ledPin=board.GP15, nPix = 60, zeroLed = 60,
                 pool = None, reverse=True,
                 posNumCol=(0,100,0), zeroCol=(100,0,0),
                 negNumCol=(0,0,100)):
        
        ledPixels.__init__(self, nPix=nPix, ledPin=ledPin)
        
        if reverse:
            self.zeroLed = zeroLed-1

        else:
            self.zeroLed = zeroLed

        self.maxLed = nPix - zeroLed
        self.minLed = -zeroLed
        self.reverse = reverse
        self.posNumCol = posNumCol
        self.zeroCol = zeroCol
        self.negNumCol = negNumCol
        
        #self.options = {
        #    "odds": self.lightOdds,
        #    "primes": self.lightPrimes}
        
    def options(self, opt):
        l_found = False
        self.off()
        for m in self.__class__.__dict__:
            #print(m)
            if opt == m:
                method = getattr(self, m)
                method()
                l_found = True
                break
        if not l_found:
            print(opt, ' not found in numberLine class')
        return l_found
    
    def lightup(self, n , col=(100,0,0)):
        if self.reverse:
            n = self.zeroLed - n
        self.light(n, col)
        
    def lightZero(self):
        self.lightup(0, col=self.zeroCol)
        
        
    def primes(self):
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
        self.lightZero()
        for n in primes:
            if n < self.maxLed:
                self.lightup(n, self.posNumCol)
                
    def odds(self):
        self.lightZero()
        for n in range(self.minLed, self.maxLed):
            if (n % 2 == 1):
                self.lightup(n, self.posNumCol)
            
    def evens(self):
        for n in range(self.minLed, self.maxLed):
            if (n % 2 == 0):
                self.lightup(n, self.posNumCol)
        self.lightZero()
        
    
    def fibonacci(self):
        fibs = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233]
        self.lightZero()
        for n in fibs:
            if n < self.maxLed:
                self.lightup(n, self.posNumCol)

    def clear(self):
        for i in range(self.nPix):
            self.lightup(i, (0,0,0))

    def reset(self):
        self.clear()
        self.lightZero()
                