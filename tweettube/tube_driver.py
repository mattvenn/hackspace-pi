#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import argparse

"""
vaccuum tube driver derived from 
https://github.com/mattvenn/arduinosketchbook/tree/master/hardwareTests/vaccuumdisplay
"""

# to use BCM pin numbers
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

#pin defs, those behind the # are for hw version 1 (option to come)
pin_clk=4 #4
pin_rst=3 #1
pin_dat=27 #21
pin_wrt=22 #22
pin_on=2 #0
pin_buz=18 #18

# set up GPIO output channel
GPIO.setup(pin_clk, GPIO.OUT)
GPIO.setup(pin_rst, GPIO.OUT)
GPIO.setup(pin_dat, GPIO.OUT)
GPIO.setup(pin_wrt, GPIO.OUT)
GPIO.setup(pin_on, GPIO.OUT)
GPIO.setup(pin_buz, GPIO.OUT)

#initial states
GPIO.output(pin_rst, GPIO.HIGH) #pull low to reset
GPIO.output(pin_clk, GPIO.LOW) #rising edge to clock
GPIO.output(pin_wrt, GPIO.LOW) #high to tell lcd to read (this because we are inverting this signal through a transistor)
GPIO.output(pin_on, GPIO.LOW) #power to display
GPIO.output(pin_buz, GPIO.LOW) #power to display

newline_code = int("0x0a",0)

def set_port(number):
	#start with clock low
	GPIO.output(pin_clk, GPIO.LOW)

	#reset port
	GPIO.output(pin_rst, GPIO.LOW)
	GPIO.output(pin_rst, GPIO.HIGH)

	#clock the data out
	for bit in reversed(range(8)):
		if number & 1 << bit:
			GPIO.output(pin_dat, GPIO.HIGH)
		else:
			GPIO.output(pin_dat, GPIO.LOW)

		#rising edge on clock to put data in
		GPIO.output(pin_clk, GPIO.HIGH)
		GPIO.output(pin_clk, GPIO.LOW)
	
	#pulse clock once more to align shift and storage registers on 595 chip
	GPIO.output(pin_clk, GPIO.HIGH)
	GPIO.output(pin_clk, GPIO.LOW)	
	
	#tell display to read it
	GPIO.output(pin_wrt, GPIO.LOW)
	GPIO.output(pin_wrt, GPIO.HIGH)
	time.sleep(0.001)
	GPIO.output(pin_wrt, GPIO.LOW)
	#display needs 1000us to do a char


def send_string(string,delay=0):
	for character in string:
		number = ord(character)
		set_port(number)
		time.sleep(delay)

def buzz():
	for i in range(1000):
		GPIO.output(pin_buz, GPIO.HIGH)
		time.sleep(0.001)
		GPIO.output(pin_buz, GPIO.LOW)
		time.sleep(0.001)
	
def display_start():	
	#turn on display, enable shift register outputs
	GPIO.output(pin_on, GPIO.HIGH)
	#wait for display to be ready
	time.sleep(0.1) 
	
	#buzz
	buzz()

	#scroll code
	set_port(int("0x13",0))

def display_finish():
	set_port(newline_code)
	#turn off display power, disable shift register outputs
	GPIO.output(pin_on, GPIO.LOW)
	#GPIO.cleanup() #this may mess with the way we left things

if __name__ == "__main__":
	argparser = argparse.ArgumentParser()
	argparser.add_argument('--hw_version',
		action='store', type=int, dest='hw_version', default="2", help="rasp pi hw version")
	argparser.add_argument('--text',
		action='store', dest='text', default="Hello World!", help="text to print")
	argparser.add_argument('--repeats',
		action='store', type=int, dest='repeats', default=3, help="number of times to repeat")

	args=argparser.parse_args()
	
	#hw_pins()
	
	display_start()

	for count in range(args.repeats):
		set_port(newline_code)
		if len(args.text)>20:
			send_string(args.text[0:20])
			time.sleep(1)
			send_string(args.text[20:],0.1)
		else:
			send_string(args.text)
		#wait till repeat
		time.sleep(3)

	display_finish()
