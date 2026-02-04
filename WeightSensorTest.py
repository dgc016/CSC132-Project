import RPi.GPIO as GPIO
import time

CS = 12
CLK = 5
DO = 6


GPIO.setmode(GPIO.BCM)
GPIO.setup(CS, GPIO.OUT)
GPIO.setup(CLK, GPIO.OUT)
GPIO.setup(DO, GPIO.IN)

def read_adc():
    value = 0
    GPIO.output(CS, GPIO.LOW)
    time.sleep(0.0001)

    for _ in range(8):
        GPIO.output(CLK, GPIO.HIGH)
        time.sleep(0.0001)

        value <<= 1
        if GPIO.input(DO):
            value |= 1

        GPIO.output(CLK, GPIO.LOW)
        time.sleep(0.0001)

    GPIO.output(CS, GPIO.HIGH)
    return value

def read_average(samples=10):
    return sum(read_adc() for _ in range(samples)) / samples

try:
    while True:
        raw = read_average(20)
        print(f"Raw ADC: {raw:.1f}")
        time.sleep(0.5)

finally:
    GPIO.cleanup()
