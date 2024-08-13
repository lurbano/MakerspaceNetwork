# Requirements:
* Raspberry Pi Pico or Pico W

# Installation
## Install Circuitpython
Download and copy the appropriate circuitpython file to the Raspberry Pi Pico (or pico W):
* For Pico: https://circuitpython.org/board/raspberry_pi_pico/
* For Pico W: https://circuitpython.org/board/raspberry_pi_pico_w/

The Pico will rename itself CIRCUITPI

## Copy files
* Copy files and folders from this repository onto the Raspberry Pi.
    * Note Sources:
        * neopixel.mpy: https://circuitpython.org/libraries
        * ledPixelsPico.py: https://github.com/lurbano/ledPixelsPico
* The Pico will run the code.py file by default. 
    * This program assumes you have a 30 pixel array (at GPIO15) and a touch sensor (at GPIO16).
    * It will run a rainbow pattern that turns on and off when you touch the touch sensor.
