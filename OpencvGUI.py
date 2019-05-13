import tkinter as tk
from tkinter import *
import cv2
from PIL import Image, ImageTk
import threading
import queue
import time
import RPi.GPIO as GPIO

## set GPIO -------
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


GPIO_TRIGGER = 4
GPIO_ECHO = 17

GPIO_BEAM = 6

GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

GPIO.setup(GPIO_BEAM, GPIO.IN)

maxWidth = 300
maxHeight = 300
lightBlue2 = "#adc5ed"
font = "Constantia"
fontButtons = (font,12)
white = "#ffffff"

mainWindow = tk.Tk()
mainWindow.configure(bg=lightBlue2)
mainWindow.geometry('%dx%d+%d+%d' % (maxWidth,maxHeight,0,0))
mainWindow.resizable(0,0)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)

Labeltk1 = Label(mainWindow, text = "Face Detected", bg ="green")
Labeltk = Label(mainWindow, text = "No Face Found", bg = "red")
faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
LabelSensor = Label(mainWindow, text = "Grip Detection", bg = "green")
LabelSensortk = Label(mainWindow, text = "No Grip Detection", bg = "red")

switch = False
Buttonpressed = True
camswitch = False

def camswitchon():
    global camswitch
    camswitch = True
    runThread()

def camswitchoff():
    global camswitch
    camswitch = False
#    cv2.destroyAllWindows()

def switchon():
    global switch
    switch = True
    ultrasonic()

def switchoff():
    global switch
    switch = False
    
def kill():
    GPIO.cleanup()
    cv2.destroyAllWindows()
    mainWindow.destroy()
    
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
            if switch == False:
                break
            elif dist > 50.0:
                LabelSensortk.place(x=150,y=10)
                LabelSensor.place_forget()
                time.sleep(0.1)
            else:
                print("Measured Distance = %.1f cm" % dist)
                LabelSensor.place(x=155,y=10)
                LabelSensortk.place_forget()
                time.sleep(0.1)
            
    thread = threading.Thread(target=run)
    thread.start()
    
def show_camera():
    while( camswitch == True):
        _, frame = cap.read()
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
        if (Buttonpressed):
            detect_face(gray)
           
            
        cv2.imshow('frame',gray)
    
#        if cv2.waitKey(1) & 0xFF == ord('q'):
        if cv2.waitKey(1) & camswitch == False:
            break
    
    cap.release()
    
def detect_face(img):
    Buttonpressed = True
    faces = faceCascade.detectMultiScale(img,1.1,5, minSize = (30,30))
#    Labeltk = Label(mainWindow, text = "No Face" , bg ="red")
#    Labeltk.place(x=7, y=70)
#    Labeltk1.place_forget()
    
    if (len(faces)) == 0:
        Labeltk.place(x=155, y=50)
    else:
        for (x, y, w, h) in faces:
            img = cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0),2)
            Labeltk1.place(x=155, y=50)
            Labeltk.place_forget()    
def runThread():
    myThread = threading.Thread(target=show_camera)
    myThread.setDaemon(False)
    myThread.start()
    
onButton = Button(mainWindow, text = "Start Grip", font=fontButtons, bg = white, width = 10 , height = 1)
onButton.configure(command = lambda: switchon())
onButton.place(x = 7, y = 7)
    
offButton = Button(mainWindow, text = "Stop Grip", font=fontButtons, bg = white, width = 10 , height = 1)
offButton.configure(command = lambda: switchoff())
offButton.place(x = 7, y = 47)
    
QuitButton = Button(mainWindow, text = "Close Gui", font=fontButtons, bg = white, width = 10 , height = 1)
QuitButton.configure(command = lambda: kill())
QuitButton.place(x = 7, y = 87)
    
CamonButton = Button(mainWindow, text = "Open Face Detect", font=fontButtons, bg = white, width = 12 , height = 1)
CamonButton.configure(command = lambda: camswitchon())
CamonButton.place(x = 7, y = 127)

CamoffButton = Button(mainWindow, text = "Close Face Detect", font=fontButtons, bg = white, width = 12 , height = 1)
CamoffButton.configure(command = lambda: camswitchoff())
CamoffButton.place(x = 7, y = 167)

mainWindow.mainloop()