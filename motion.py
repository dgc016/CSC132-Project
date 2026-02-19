import time
import random

# Try to import Raspberry Pi libraries
try:
    import RPi.GPIO as GPIO
    from gpiozero import MotionSensor
    import Weight
    PI_MODE = True
except ModuleNotFoundError:
    PI_MODE = False


# =====================================================
# RASPBERRY PI MODE (Real Sensors)
# =====================================================
if PI_MODE:

    SENSOR_PIN = 26
    LED_PIN = 27

    motionSensor = MotionSensor(SENSOR_PIN)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN, GPIO.OUT)

    _started = False

    def start_motion_system():
        """
        Called once after login.
        Initializes weight system.
        """
        global _started
        if not _started:
            Weight.start()
            _started = True

    def detect_mail_once(weight_threshold=2.0):
        """
        Returns:
        (mail_detected: bool, weight_value: float, motion: bool)
        """
        motion = bool(motionSensor.motion_detected)
        weight_value = Weight.get_weight_value()
        has_weight = weight_value > weight_threshold

        if motion and has_weight:
            GPIO.output(LED_PIN, GPIO.HIGH)
            return True, weight_value, motion
        else:
            GPIO.output(LED_PIN, GPIO.LOW)
            return False, weight_value, motion

    def cleanup():
        GPIO.cleanup()


# =====================================================
# Fake Sensors for Testing GUI
# =====================================================
else:

    print("Running in FAKE SENSOR MODE (No Raspberry Pi detected)")

    def start_motion_system():
        """
        Nothing needed for fake mode.
        """
        pass

    def detect_mail_once(weight_threshold=2.0):
        """
        Simulates random mail arrivals for GUI testing.
        """
        time.sleep(0.2)

        # 4% chance of fake mail arrival each cycle
        if random.random() < 0.04:
            fake_weight = random.uniform(10, 120)  # grams
            return True, fake_weight, True
        else:
            return False, 0.0, False

    def cleanup():
        pass
