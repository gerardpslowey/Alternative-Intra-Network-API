import RPi.GPIO as GPIO
import time
import threading

GPIO.setwarnings(False)
# Use BOARD mode to address numbers
GPIO.setmode(GPIO.BOARD)

##############################################
####### Assigning Components to Pins #########
##############################################

############# Buzzer #############
# Buzzer is on pin 10
BUZZER = 10
GPIO.setup(BUZZER, GPIO.OUT, initial=GPIO.HIGH)  # Pin 10 as output

######### PIR Sensor ############
# PIR sensor is on pin 13
PIR = 13
LED = 3
GPIO.setup(PIR, GPIO.IN)  # Read output from PIR motion sensor
GPIO.setup(LED, GPIO.OUT)  # LED output pin

####### Motor for pump ##########
# Pin 33 controls the motor speed
MOTORSPEED = 33
GPIO.setup(MOTORSPEED, GPIO.OUT)  # Set it as an output pin

# Ultrasonic Sensor
TRIGGER = 8  # Trigger is on pin 8
ECHO = 26  # Echo on pin 26
GPIO.setup(TRIGGER, GPIO.OUT)


def pir_motion_senor_and_led_with_buzzer():
    while True:
        i = GPIO.input(PIR)

        if i == 0:
            # When output from motion sensor is LOW
            print("No people detected", i)
            GPIO.output(3, 0)  # Turn OFF LED
            GPIO.output(BUZZER, GPIO.HIGH)  # Turn the buzzer off
            time.sleep(0.1)

        elif i == 1:
            # When output from motion sensor is HIGH
            print("Person detected", i)
            GPIO.output(LED, 1)  # Turn ON LED
            GPIO.output(BUZZER, GPIO.LOW)  # Sound the buzzer
            time.sleep(1)


def ultrasonic_sensor_and_motor():

    # PWM frequency is 100Hz
    motorSpeed = GPIO.PWM(MOTORSPEED, 100)
    # Start with a duty cycle of zero (it’s off)
    motorSpeed.start(0)

    # Trig is set as output
    GPIO.output(TRIGGER, 0)  # Set to low

    GPIO.setup(ECHO, GPIO.IN)
    # Echo is set as input

    time.sleep(0.1)
    # time delay for the sensor to settle, needs at least 15ms

    GPIO.output(TRIGGER, 1)
    # Next three lines creates the 10µs pulse
    time.sleep(0.00001)
    GPIO.output(TRIGGER, 0)

    while GPIO.input(ECHO) == 0:
        # Stops motor when the sensor reads normal again
        motorSpeed.stop()

    while GPIO.input(ECHO) == 1:
        # Change the speed when the hand is sensed.
        # <speed> is any number between 1-100, 100 is the #fastest.
        motorSpeed.ChangeDutyCycle(10)


if __name__ == '__main__':
    try:
        pass

    except KeyboardInterrupt:
        print("System Stopped")
        GPIO.cleanup()
