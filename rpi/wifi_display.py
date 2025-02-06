# Import Python System Libraries
import time
# Import Blinka Libraries
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
# Import the SSD1306 module.
import adafruit_ssd1306
from wifi import Cell, Scheme
import os
import subprocess
import time
import re

# Create the I2C interface.

def filter_ssid(cell):
	if cell.ssid == "UWNet" or cell.ssid == "Chota Bhai":
		return True
	else:
		return False

i2c = busio.I2C(board.SCL, board.SDA)

# 128x32 OLED Display
reset_pin = DigitalInOut(board.D4)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, reset=reset_pin)
# Clear the display.
display.fill(0)
display.show()
width = display.width
height = display.height


os.system('nmcli dev wifi rescan')

wifilist = subprocess.check_output(['nmcli', 'dev' ,'wifi' ,'list'])
if "UWNet" in str(wifilist):
  os.system('nmcli dev wifi connect UWNet')
else:
  os.system('nmcli dev wifi connect Blaine-Calf-2G password M@d1675Wi$')



IPAddr = re.search('([0-9]{1,3}\.?){4}',str(subprocess.check_output(['hostname','-I'])))
output = str(subprocess.check_output(['sudo', 'iwgetid']))
display.text("Connected: " + output.split('"')[1],0,0,1)
display.text("IP: " + IPAddr[0] , 0,10,1)
display.show()

