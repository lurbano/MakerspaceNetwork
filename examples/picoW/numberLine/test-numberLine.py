import board
from numberLine import *

numLine = numberLine(ledPin = board.GP27, nPix=60, zeroLed=0, reverse=True)

numLine.options('primes')

