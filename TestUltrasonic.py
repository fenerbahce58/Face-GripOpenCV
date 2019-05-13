import tkinter as tk
import threading
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO_TRIGGER = 4
GPIO_ECHO = 17

GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

switch = False
root = tk.Tk()

def switchon():
    global switch
    switch = True
    ultrasonic()

def switchoff():
    global switch
    switch = False
    
def kill():
    GPIO.cleanup()
    root.destroy()
    
def distance():
    GPIO.output(GPIO_TRIGGER, True)
    
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    
    StartTime = time.time()
    StopTime = time.time()
    
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
        
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
        
    
    TimeElapsed = StopTime - StartTime
    
    distance = (TimeElapsed * 34300) / 2
    
    return distance

def ultrasonic():
    def run():
        while (switch == True):
            dist = distance()
            print("Measured Distance = %.1f cm" % dist)
            time.sleep(0.1)
            if switch == False:
                break
    thread = threading.Thread(target=run)
    thread.start()
    
onbutton = tk.Button(root, text = "Start", command = switchon)
onbutton.pack()
offbutton = tk.Button(root, text = "Stop", command = switchoff)
offbutton.pack()
killbutton = tk.Button(root, text = "Exit", command = kill)
killbutton.pack()
root.mainloop()
    