# Import Python System Libraries
import time
# Import Blinka Libraries
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
# Import the SSD1306 module.
import adafruit_ssd1306
# Import RFM9x
import adafruit_rfm9x
import os
from datetime import datetime
import sys

#import sql libraries
import pyodbc
server = 'airsensors.database.windows.net'
database = 'airsensorsdb'
username = ''
password = ''
driver = 'FreeTDS'

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# 128x32 OLED Display
reset_pin = DigitalInOut(board.D4)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, reset=reset_pin)
# Clear the display.
display.fill(0)
display.show()
width = display.width
height = display.height

# Configure LoRa Radio
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 915.0)
rfm9x.tx_power = 23
rfm9x.preamble_length = 8
rfm9x.spreading_factor = 7
rfm9x.signal_bandwidth = 500000 
prev_packet = None
values = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
print(rfm9x.enable_crc)
while True:
    print("new iteration\n")
    packet = None
    # draw a box to clear the image
    display.fill(0)
    devices = [1,2]
    for device in devices:
      #start transaction with device
      print("sending permission to device" + str(device))
      print(device.to_bytes(1,'little'))
      rfm9x.send(device.to_bytes(1, 'little'))
      
      # check for packet rx
      packet = rfm9x.receive(timeout = 1)
      if packet is None:
          display.show()
          
          display.text('- Waiting for PKT - dev ' + device, 15, 20, 1)
         
      else:
          print("packet rx from device " + str(device) + "\n")
          #convert bytes to integer values
          for i  in range(0,27,2):
            
              values[int(i/2)] = int.from_bytes(packet[i:i+2],'little')
              
          if values[0] == 9876:   
            # Display the packet text and rssi
            display.fill(0)
            prev_packet = packet
             # packet_text = str(int.from_bytes(prev_packet[8:9],'little'))
            packet_text1 = ""
            packet_text2 = ""
            filetext = datetime.now().strftime('%H:%M:%S') + ","
            sqltext = ""
            for i in range(1,9):
              packet_text1 = packet_text1 + " " + str(values[i])
            for i in range (9,14):
              packet_text2 = packet_text2 + " " + str(values[i])
            for i in range (1,14):
              filetext = filetext + str(values[i]) + ","
              sqltext = sqltext + ","+str(values[i])
              
            display.text('RX: ', 0, 0, 1)
            display.text(packet_text1, 25, 0, 1)
            display.text(packet_text2, 25, 8, 1)
            print(sqltext)
            okay = 9
            ack =  okay.to_bytes(1, 'little')
          
            rfm9x.send(ack)
            print("adding data to file\n")
            #if file does not exist yet, create it.
            filename = "gasanalyzerdata/"+"dev-"+str(device)+"_"+datetime.now().strftime("%m-%d-%Y")+".csv"
            if os.path.isfile(filename) == False:
              f = open(filename,"x")
              print("new file created\n")
              f.write("Timestamp,mq-2,mq-3,mq-4,mq-5,mq-6,mq-7,mq-8,mq-9,mq-135,mq-136,mq-137,mq-138\n")
              f.close
              print("new file written")
            #open file, add data and close
            f = open(filename,'a')
            f.write(filetext)
            f.write("\n")  
            f.close()
            
            print("File IO Done for device " + str(device))
            datestr = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  
            try:
              cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password + ';TDS_Version=8.0')
              cnxn.timeout = 3
              cursor = cnxn.cursor()
              cursor.execute("INSERT INTO newdevices (date_time, device_ID, IR, MQ8, MQ138, MQ5, MQ135, MQ6, MQ7, MQ4, MQ137, MQ9, MQ3, MQ136, MQ2) "+ "VALUES" + " ('" +datestr+"'," + str(device)  +sqltext+")")
              cnxn.commit()
              print("database updated\n")
            except pyodbc.Error:
              print("err")
        
    display.show()
    time.sleep(0.5)
