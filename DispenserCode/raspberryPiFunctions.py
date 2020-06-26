# Need to save the values taken from these sensors to log.JSON
# Should be in the form:
'''
{
    "currentVolume": 0,
    "dispenses": [
      {
        "time": "14:51:18",
        "volume": 1.2
      },
      {
        "time": "14:51:28",
        "volume": 1.2
      },
      {
        "time": "14:52:00",
        "volume": 1.2
      },
      {
        "time": "14:52:08",
        "volume": 1.2
      }
    ],
    "total_detected": 5,
    "total_dispensed": 4,
    "total_ignores": 1
}
'''

import json

import RPi.GPIO as GPIO
import time
from threading import Thread
from datetime import date, datetime

GPIO.setwarnings(False)
# Use BOARD mode to address pin numbers
GPIO.setmode(GPIO.BOARD)

##############################################
####### Assigning Components to Pins #########
##############################################

############# Buzzer #############
BUZZER = 10  # Buzzer is on pin 10
GPIO.setup(BUZZER, GPIO.OUT, initial=GPIO.HIGH)  # Pin is output, initially set to off

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

today = str(date.today().strftime("%d-%m-%Y"))
todays_log = today + "Log"


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
            time.sleep(1)
            GPIO.output(LED, 0)  # Turn OFF LED

            GPIO.output(BUZZER, GPIO.LOW)  # Sound the buzzer
            time.sleep(1)
            GPIO.output(BUZZER, GPIO.HIGH)  # Turn the buzzer off

            update_json_parameters(["total_detected", "total_ignores"])


def ultrasonic_sensor_and_motor():
    while True:
        # At start of each listen
        GPIO.output(TRIGGER, 0)  # Set to low
        time.sleep(0.1)

        # Place holders for timing data
        start = 0
        stop = 0

        GPIO.output(TRIGGER, 1)  # Send pulse to the sensor,
        time.sleep(0.00001)  # Sensor should return sonic burst
        GPIO.output(TRIGGER, 0)  # Then reset to 0

        while GPIO.input(ECHO) == 0:
            pass  # Don't do anything
            start = time.time()

        while GPIO.input(ECHO) == 1:
            pass
            stop = time.time()
            total_time = stop - start

            # Stop - Start * half the distance of sound
            distance = total_time * 170

            # 250mm of a distance between sensor and dispenser drip tray
            if distance < 0.25:
                # <speed> is any number between 1-100, 100 is the fastest.
                motorSpeed.ChangeDutyCycle(40)  # Changing Speed and starting the motor
                time.sleep(0.9)  # Run motor for 0.9 seconds to dispense 1.2ml through 3ml tube
                motorSpeed.stop()  # Stops motor when the sensor reads normal again

                # Record the dispense in the usage log
                write_to_usage_json()
                # Prevent update collisions
                time.sleep(1)
                # Update the dispensed counter
                update_json_parameters("total_dispensed")


######################################################
########## Functions to update device logs ###########
######################################################

# function to add to JSON list
def write_to_usage_json(data, filename='log.json'):
    current_time = str(datetime.now().strftime('%H:%M:%S'))

    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

    with open(filename) as json_file:
        data = json.load(json_file)

        temp = data['dispenses']

        # python object to be appended to dispenses array
        d = {"time": current_time,
             "volume": "1.2ml"
             }

        # appending data to temp_details
        temp.append(d)

    write_to_usage_json(data)


def update_json_parameters(*parameters, filename='log.json'):
    try:
        # Open in reading and writing mode
        with open(filename, "r+") as device_log:
            log = json.load(device_log)

            # Increment the parameters
            for parameter in parameters:
                if parameter == "total_detected":
                    log[parameter] += 1
                elif parameter == "total_dispensed":
                    log[parameter] = len(log['dispenses'])
                elif parameter == "total_ignores":
                    log[parameter] = int(log['total_detected']) - int(log['total_dispensed'])

        # Dump the changes back to the json file
        with open(filename, "w") as device_log:
            json.dump(log, device_log)

    except Exception as e:
        print("Error: {}".format(e))


# Code that would get executed to get data from weight cell
# Available at https://github.com/tatobari/hx711py
# To execute properly a reference unit calculation is needed
# This is explained in the relevant part of the electronics documentation

'''
def weight_cell_get_weight():

    EMULATE_HX711 = False

    referenceUnit = 1

    if not EMULATE_HX711:
        import RPi.GPIO as GPIO
        from HX711.hx711 import HX711
    else:
        from HX711.hx711 import HX711

    def cleanAndExit():
        print("Cleaning...")

        if not EMULATE_HX711:
            GPIO.cleanup()

        print("Bye!")
        sys.exit()

    hx = HX711(5, 6)

    # I've found out that, for some reason, the order of the bytes is not always the same between versions of python, numpy and the hx711_files itself.
    # Still need to figure out why does it change.
    # If you're experiencing super random values, change these values to MSB or LSB until to get more stable values.
    # There is some code below to debug and log the order of the bits and the bytes.
    # The first parameter is the order in which the bytes are used to build the "long" value.
    # The second paramter is the order of the bits inside each byte.
    # According to the HX711 Datasheet, the second parameter is MSB so you shouldn't need to modify it.
    hx.set_reading_format("MSB", "MSB")

    # HOW TO CALCULATE THE REFFERENCE UNIT
    # To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
    # In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
    # and I got numbers around 184000 when I added 2kg. So, according to the rule of thirds:
    # If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.
    # hx.set_reference_unit(113)

    # Need actual cell to get referenceUnit
    hx.set_reference_unit(referenceUnit)

    hx.reset()

    hx.tare()

    print("Tare done! Add weight now...")

    # to use both channels, you'll need to tare them both
    # hx.tare_A()
    # hx.tare_B()

    while True:
        try:
            # These three lines are usefull to debug wether to use MSB or LSB in the reading formats for the first
            # parameter of "hx.set_reading_format("LSB", "MSB")". Comment the two lines "val = hx.get_weight(5)" and
            # "print val" and uncomment these three lines to see what it prints.

            # np_arr8_string = hx.get_np_arr8_string()
            # binary_string = hx.get_binary_string()
            # print binary_string + " " + np_arr8_string

            # Prints the weight. Comment if you're debbuging the MSB and LSB issue.
            val = hx.get_weight(5)
            print(val)

            # To get weight from both channels (if you have load cells hooked up
            # to both channel A and B), do something like this
            # val_A = hx.get_weight_A(5)
            # val_B = hx.get_weight_B(5)
            # print "A: %s  B: %s" % ( val_A, val_B )

            hx.power_down()
            hx.power_up()
            time.sleep(0.1)

        except (KeyboardInterrupt, SystemExit):
            cleanAndExit()
'''

if __name__ == '__main__':
    try:
        # Run the sensor monitoring software in seperate threads concurrently
        Thread(target=pir_motion_senor_and_led_with_buzzer).start()
        Thread(target=ultrasonic_sensor_and_motor).start()
        # Thread(target=weight_cell_get_weight).start()

    # trap a CTRL+C keyboard interrupt
    except KeyboardInterrupt:
        print("System Stopped")
        GPIO.cleanup()  # resets all GPIO ports used by this program
