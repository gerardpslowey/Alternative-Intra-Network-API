import RPi.GPIO as GPIO
import time
from threading import Thread

GPIO.setwarnings(False)
# Use BOARD mode to address numbers
GPIO.setmode(GPIO.BOARD)

##############################################
####### Assigning Components to Pins #########
##############################################

############# Buzzer #############
BUZZER = 10  # Buzzer is on pin 10
GPIO.setup(BUZZER, GPIO.OUT, initial=GPIO.LOW)  # Pin is output, initially set to off

######### PIR Sensor ############
PIR = 13  # PIR sensor is on pin 13
GPIO.setup(PIR, GPIO.IN)  # Read output from PIR motion sensor

######## LED ####################
LED = 3  # LED is on pin 3
GPIO.setup(LED, GPIO.OUT)  # LED output pin

####### Motor for pump ##########
MOTOR = 33  # Pin 33 controls the motor speed
GPIO.setup(MOTOR, GPIO.OUT)  # Set it as an output pin
motorSpeed = GPIO.PWM(MOTOR, 100)  # PWM frequency is 100Hz on MOTOR pin
motorSpeed.start(0)  # Start with a duty cycle of zero (it’s off)

# Ultrasonic Sensor
TRIGGER = 8  # Trigger is on pin 8
ECHO = 26  # Echo on pin 26
GPIO.setup(TRIGGER, GPIO.OUT)  # Trig is set as output
GPIO.setup(ECHO, GPIO.IN)  # Echo is set as input


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
    while True:
        if GPIO.input(ECHO) == 0:
            GPIO.output(TRIGGER, 0)  # Set to low
            motorSpeed.stop()
            # Stops motor when the sensor reads normal again

        elif GPIO.input(ECHO) == 1:
            # <speed> is any number between 1-100, 100 is the fastest.
            motorSpeed.start(25)  # Motor will run at slow speed
            GPIO.output(TRIGGER, 1)  # Set to high


if __name__ == '__main__':
    try:
        Thread(target=pir_motion_senor_and_led_with_buzzer).start()
        Thread(target=ultrasonic_sensor_and_motor).start()

    # trap a CTRL+C keyboard interrupt
    except KeyboardInterrupt:
        print("System Stopped")
        GPIO.cleanup()  # resets all GPIO ports used by this program
