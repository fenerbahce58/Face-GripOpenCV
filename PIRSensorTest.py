import tkinter as tk
from tkinter import *
import RPi.GPIO as GPIO
import time
import threading

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN)

switch = False
switchb = False
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

LabelPir = Label(mainWindow, text = "Motion Detected", bg = "green")
LabelPirDelay = Label(mainWindow, text = "Delay", bg = "orange")
LabelPirtk = Label(mainWindow, text = "No Motion", bg = "red")

def switchon():
    global switch
    switch = True
    testPir()

def switchoff():
    global switch
    switch = False
    
def testPir():
    def run():
        while (switch == True):
            if switch == False:
                break
            elif GPIO.input(23):
                LabelPirtk.place_forget()
#                LabelPirDelay.place_forget()
                LabelPir.place(x=155,y=10)
                time.sleep(4)
            else:
               delayfunc()
                
        
    thread = threading.Thread(target=run)
    thread.start()
def delayfunc():
    LabelPir.place_forget()
#                LabelPirDelay.place(x=155,y=10)
#                time.sleep(3)
    LabelPirDelay.place(x=155, y=10)
    time.sleep(6)
    LabelPirDelay.place_forget()
    LabelPirtk.place(x=155, y=10)
def closegui():
    mainWindow.destroy()
    
onButton = Button(mainWindow, text = "Start Grip", font=fontButtons, bg = white, width = 10 , height = 1)
onButton.configure(command = lambda: switchon())
onButton.place(x = 7, y = 7)
    
offButton = Button(mainWindow, text = "Stop Grip", font=fontButtons, bg = white, width = 10 , height = 1)
offButton.configure(command = lambda: switchoff())
offButton.place(x = 7, y = 47)

closeButton = Button(mainWindow, text = "Close GUI", font=fontButtons, bg = white, width = 10 , height = 1)
closeButton.configure(command = lambda: closegui())
closeButton.place(x = 7, y = 87)  

mainWindow.mainloop()