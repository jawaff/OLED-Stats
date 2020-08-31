#!/usr/bin/python3
#-----------------------------------------------------------
#    ___  ___  _ ____
#   / _ \/ _ \(_) __/__  __ __
#  / , _/ ___/ /\ \/ _ \/ // /
# /_/|_/_/  /_/___/ .__/\_, /
#                /_/   /___/
#
# Project : Pi-Hole Status Screen
# File    : stats.py
#
# Script to provide a status screen for a Pi-Hole system.
# Requires an I2C OLED screen, momentary button and an LED with current limiting resistor.
#
# Author : Matt Hawkins
# Date   : 15/10/2019
# Source : https://bitbucket.org/MattHawkinsUK/rpispy-misc/src/master/pihole/
#
# Additional details here:
# https://www.raspberrypi-spy.co.uk/
#
# gpiozero Button reference:
# https://gpiozero.readthedocs.io/en/stable/recipes.html#button
#
# gpiozero LED PWM reference:
# https://gpiozero.readthedocs.io/en/stable/recipes.html#led-with-variable-brightness
#
#-----------------------------------------------------------

# Standard libraries
import time
import math
import json
import requests
import subprocess

# Graphics libraries
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# Adafruit library for I2C OLED screen
import Adafruit_SSD1306

# GPIOZero functions for buttons and LEDs
from gpiozero import Button
#from gpiozero import PWMLED

def button_presssed():
  global mode
  if mode==1:
    mode=0
  else:
    mode=1

# Define GPIO pins used by button and LED
ButtonGPIO=21
LEDGPIO=24

# Configure button connected to GPIO21 (Pin 40) and Ground (Pin 39)
button = Button(ButtonGPIO)
button.when_pressed = button_presssed

# Configure LED connected to GPIO24 (Pin 18) and Ground (Pin 20)
#led = PWMLED(LEDGPIO)
#led.value=0

# 128x64 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=None)
# disp = Adafruit_SSD1306.SSD1306_128_64(rst=None, i2c_address=0x3C)
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=None, i2c_bus=2)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
home_image = Image.open('/home/pi/stats/landscape_deer.jpg').resize((disp.width, disp.height), Image.ANTIALIAS).convert('1')
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = 0
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load Truetype font from https://www.dafont.com/bitmap.php
# VCR OSD Mono by Riciery Leal
font = ImageFont.truetype('/home/pi/stats/VCR_OSD_MONO_1.001.ttf',20)
font2 = ImageFont.truetype('/home/pi/stats/VCR_OSD_MONO_1.001.ttf',40)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)
# Show Start Script text
draw.text((x, top), "Starting...",  font=font, fill=255)
disp.image(image)
disp.display()

# Default mode, show large percentage
mode=0
counter=1

while True:

  # As counter cycles from 1-30 we generate LED value
  #led.value=counter/30
  
  if mode==0 and counter>29:
    disp.image(home_image)
    disp.display()
    counter=0
    
  if mode==1:
    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0) 
    
    # Get system data
    # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    cmd = "hostname -I | cut -d\' \' -f1"
    IP = subprocess.check_output(cmd, shell = True )
    
    # Get system data
    # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    cmd = "top -bn1 | grep load | awk '{printf \"C: %.2f%%\", $(NF-2)}'"
    CPU = subprocess.check_output(cmd, shell = True )
    cmd = "free -m | awk 'NR==2{printf \"M: %s/%sMB\", $3,$2 }'"
    MemUsage = subprocess.check_output(cmd, shell = True )

    for i in range(10):
        offset = (i-2)*10 if i > 2 else 0
        # Display system stats    
        draw.text((x-offset, top+2),       str(IP.decode('UTF-8')),  font=font, fill=255)
        draw.text((x-offset, top+24),    str(CPU.decode('UTF-8')), font=font, fill=255)
        draw.text((x-offset, top+46),    str(MemUsage.decode('UTF-8')), font=font, fill=255)

        # Display image.
        disp.image(image)
        disp.display()
        time.sleep(1)

        # Draw a black filled box to clear the image.
        draw.rectangle((0,0,width,height), outline=0, fill=0) 

    # Get system data
    # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    cmd = "free -m | awk 'NR==2{printf \"M: %s/%sMB\", $3,$2 }'"
    MemUsage = subprocess.check_output(cmd, shell = True )
    cmd = "df -h | awk '$NF==\"/\"{printf \"D: %d/%dGB\", $3,$2}'"
    MainDisk = subprocess.check_output(cmd, shell = True )
    cmd = "df -h | awk '$NF==\"/mnt/storage\"{printf \"P: %sB/%sB\", $3,$2}'"
    PlexDisk = subprocess.check_output(cmd, shell = True )


    for i in range(10):
        offset = (i-2)*10 if i > 2 else 0
        # Display system stats    
        draw.text((x-offset, top+2),       str(IP.decode('UTF-8')),  font=font, fill=255)
        draw.text((x-offset, top+24),    str(MainDisk.decode('UTF-8')),font=font, fill=255)
        draw.text((x-offset, top+46),    str(PlexDisk.decode('UTF-8')),font=font, fill=255)

        # Display image.
        disp.image(image)
        disp.display()
        time.sleep(1)
        
        # Fills screen with black.
        draw.rectangle((0,0,width,height), outline=0, fill=0) 
    
    mode=0
    counter=29

  counter=counter+1
  time.sleep(1)
