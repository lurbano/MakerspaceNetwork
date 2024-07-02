import network
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led
import machine
import json

ssid = 'TFS Students'
password = 'Fultoneagles'

import stepper
IN1 = 11
IN2 = 10
IN3 = 9
IN4 = 8
stepper_motor = stepper.HalfStepMotor.frompins(IN1, IN2, IN3, IN4)
stepper_motor.reset()

from DCMotor import *
import time

Topright = DCMotor(1,2)
Bottomright = DCMotor(5,6)
Topleft = DCMotor(12,13)
Bottomleft = DCMotor(14,15)

def Ramp():
    stepper_motor.step(500)
    sleep(0.5)
    stepper_motor.step(-500)

def rightforwardstop():
    Topright.stop()
    Bottomright.stop()
    
def rightforward():
    Topright.forward()
    Bottomright.backward()
    
def leftforwardstop():
    Topleft.stop()
    Bottomleft.stop()
    
def leftforward():
    Topleft.backward()
    Bottomleft.forward()
  
def leftbackwardstop():
    Topleft.stop()
    Bottomleft.stop()
    
def leftbackward():
    Topleft.forward()
    Bottomleft.backward()
    
def rightbackwardstop():
    Topright.stop()
    Bottomright.stop()

def rightbackward():
    Topright.backward()
    Bottomright.forward()
      
def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    print(wlan.ifconfig())
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    print(f"http://{ip}")
    return ip

def open_socket(ip):
    # Open a socket
    address = (ip,80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen()
    return(connection)
 
def webpage(temperature, state):
    #Template HTML
    with open("index.html","r") as f:
        html = f.read()
    return str(html)

def serve(connection):
    #Start a web server
    state = 'OFF'
    pico_led.off()
    temperature = 0
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        print("Request:", request)
        try:
            requestType = request.split()[0][2:]
            print("type:", requestType)
            
            if requestType == "GET":
                request = request.split()[1]
            
            if requestType == "POST":
                postRequest = "{" + request.split()[-1].split('{')[-1][:-1]
                print("postRequest 1: ", postRequest)
                postRequest = json.loads(postRequest)
                print("postRequest: ", postRequest)
            
        except IndexError:
            print("Error")
            pass
        if requestType == "GET":
            if request == '/lighton?':
                pico_led.on()
                state = 'ON'
            elif request =='/lightoff?':
                pico_led.off()
                state = 'OFF'
            if request =='/rightforward?':
                rightforward()
            if request =='/rightstop?':
                rightforwardstop()
            if request =='/rightbackward?':
                rightbackward()
            if request =='/leftforward?':
                leftforward()
            if request =='/leftbackward?':
                leftbackward()
            if request =='/leftstop?':
                leftforwardstop()

            if request =='/Ramp?':
                Ramp()
            temperature = pico_temp_sensor.temp
            html = webpage(temperature, state)
            client.send(html)
            client.close()
            
        elif requestType == "POST":
            action = postRequest["action"]
            if action == "rightforwardStart":
                rightforward()
            elif action == "rightforwardStop":
                rightforwardstop()
            elif action == "rightbackwardStart":
                rightbackward()
            client.close()


try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()