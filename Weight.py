import RPi.GPIO as GPIO
import time
import Pushover

DT = 23
SCK = 20

GPIO.setmode(GPIO.BCM)
GPIO.setup(DT, GPIO.IN)
GPIO.setup(SCK, GPIO.OUT)
GPIO.output(SCK, False)

offset = 0
scale = 1000

def readRaw():
    while GPIO.input(DT) == 1:
        time.sleep(0.0001)

    count = 0
    for _ in range(24):
        GPIO.output(SCK, True)
        count = count << 1
        GPIO.output(SCK, False)
        if GPIO.input(DT):
            count += 1

    # Set gain to 128
    GPIO.output(SCK, True)
    GPIO.output(SCK, False)

    # Convert to signed value
    if count & 0x800000:
        count -= 0x1000000

    return count

def calibrate(samples=20):
    print("Calibrating... Remove all weight.")
    total = 0
    for i in range(samples):
        total += readRaw()
        time.sleep(0.1)
    return total / samples

def start():
    try:
        global offset
        input("Press Enter to calibrate (no weight on scale)...")
        offset = calibrate()
        print("Scale ready.")
    except:
        print("An error has occured.")

def weigh():
    global offset
    raw = readRaw()
    weight = (offset - raw) / scale
    print(f"Weight: {weight:.2f}")
    time.sleep(1)
    if (weight > 2):
        return True
    else:
        return False
    time.sleep(1)
