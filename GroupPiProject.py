#import sensor
from gpiozero import MotionSensor
from time import sleep
import RPi.GPIO as GPIO
import Pushover
import Weight



#assign pin num for sensor
sensorpin = 26

#light to say that there is something in the box
ledpin = 27


motionSensor = MotionSensor(sensorpin)



GPIO.setmode(GPIO.BCM)
GPIO.setup(ledpin,GPIO.OUT)
Weight.start()
print("start done")

try:
    #detect motion
    while(True):
        hasWeight = Weight.weigh()
       
        if(motionSensor.motion_detected and hasWeight):
           
            Pushover.run()
            print("Package in mailbox.")
            GPIO.output(ledpin,GPIO.HIGH)
            sleep(60)
            #sends text to SMS (set this up after friday)
           
        else:
            GPIO.output(ledpin,GPIO.LOW)
           
        sleep(0.1)
except KeyboardInterrupt:  #CTRL-C
    print("Stopping Program.")
    GPIO.cleanup()
