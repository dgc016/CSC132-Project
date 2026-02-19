# Weight.py
import RPi.GPIO as GPIO
import time

DT = 23
SCK = 20

offset = 0.0
scale = 1000.0   # keep your scale factor; adjust if needed
_initialized = False


def _setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DT, GPIO.IN)
    GPIO.setup(SCK, GPIO.OUT)
    GPIO.output(SCK, False)


def readRaw():
    # wait until HX711 is ready (DT goes LOW)
    while GPIO.input(DT) == 1:
        time.sleep(0.0001)

    count = 0
    for _ in range(24):
        GPIO.output(SCK, True)
        count = count << 1
        GPIO.output(SCK, False)
        if GPIO.input(DT):
            count += 1

    # set gain to 128 (1 extra clock)
    GPIO.output(SCK, True)
    GPIO.output(SCK, False)

    # convert to signed
    if count & 0x800000:
        count -= 0x1000000

    return count


def calibrate(samples=20, delay=0.05):
    """
    Take readings with no weight on the scale and compute offset.
    """
    total = 0
    for _ in range(samples):
        total += readRaw()
        time.sleep(delay)
    return total / samples


def start(samples=20):
    """
    Call once after login (or when GUI starts sensors).
    Auto-calibrates (tare) assuming scale is empty.
    """
    global offset, _initialized
    if _initialized:
        return True

    try:
        _setup_gpio()
        offset = calibrate(samples=samples)
        _initialized = True
        return True
    except Exception:
        return False


def get_weight_value():
    """
    Returns a numeric weight value.
    """
    global offset
    raw = readRaw()
    weight = (offset - raw) / scale
    return float(weight)


def has_mail(threshold=2.0):
    """
    Returns True/False based on weight threshold.
    """
    return get_weight_value() > threshold
