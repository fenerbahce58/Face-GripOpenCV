import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO_BEAM = 17

GPIO.setup(GPIO_BEAM, GPIO.IN)

while True:
    if (GPIO.input(GPIO_BEAM) == 1):
        print("Not Broken")
        time.sleep(1)
    if (GPIO.input(GPIO_BEAM) == 0):
        print("Beam Broken")
        time.sleep(1)