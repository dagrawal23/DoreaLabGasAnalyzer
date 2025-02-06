# Raspberry pi

The pi folder contains all python scripts needed for the pi to correctly work.
wifi_display.py - displays IP address on bootup (useful for ssh if needed)
single_device_lora.py - communicates with a single node over lora
multidevice_lora.py - communicates with multiple node over lora, number of nodes and ids need to be hardcoded
raspi-blinka.py - python script install blinka - which is a dependency for running circuitpython libraries, visit - https://circuitpython.org/ , https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/running-circuitpython-code-without-circuitpython for more info
test-db and other scripts are just testing scripts that may no longer work. The pi is supposed to upload coollected data to an Azure SQL database in addition to storing it locally. Some setup needs to be done to get the database storage working correctly.

#Arduino

The single sketch does everything - reads ADC, sends data over UART. Also the id of node needs to be hardcoded in this sketch and flashed on each device. So need to be mindful of id conflicts before flashing/reflashing devices. 