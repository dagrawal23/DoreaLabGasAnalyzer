# Gas Analyzer

## Core Components

- **MQ Sensor Device**  
  - Powered by [Feather M0 RFM9x](https://www.adafruit.com/product/3178)

- **PCB Files**  
  - Altium project in this repository

- **Parts List**  
  - BOM spreadsheet in this repository

- **Raspberry Pi Cluster Node**  
  - Raspberry Pi 4B + Adafruit LoRa Bonnet  
  - [Buy the LoRa Bonnet](https://www.adafruit.com/product/4074)

## Overview

A **Cluster** consists of one Raspberry Pi (the _Coordinator_) and multiple Sensor Nodes.

- **Device Nodes**  
  - Each node has a **unique integer ID** (unique across all clusters and devices).  
  - Must be flashed with its assigned Coordinator (Pi) ID to join the cluster.

- **Coordinator (Raspberry Pi)**  
  - Also has its own **unique integer ID** (distinct from all device IDs).  
  - Maintains a list of Device Node IDs it manages.  

see image.png for an infographic on this structure

## To start data collection
- Double Click the Gas Analyzer icon on the Desktop of your Pi
- A dialog box will pop up
- Click Execute
## Setting up a New Pi

1. **Acquire & Assemble**  
   - Get a Raspberry Pi 4B, a protective case, and the official Raspberry Pi 7" Touch Display.  
   - Attach the Adafruit LoRa Bonnet, mount the Pi inside the case, and connect the display.

2. **Clone an Existing SD Card**  
   - Install [Balena Etcher](https://www.balena.io/etcher/).  
   - Insert the source SD card (already set up) into your computer.  
   - Launch Balena Etcher:  
     1. **Flash from file** → choose the source card’s image.  
     2. **Select target** → the new SD card.  
     3. Click **Flash!** and wait for completion.

3. **Configure the New Pi**  
   - Boot the new Pi with the cloned SD card.  
   - Open `/home/rpi/radio_communication_gui.py` in your favorite editor.  
     - Find the list named `devices`:  
       ```python
       devices = [ … ]
       ```
       Replace its contents with the integer IDs of your sensor nodes.  
     - In the `poll_devices` function, locate:  
       ```python
       if values[0] == 9876:
       ```
       Replace `9876` (the old Pi ID) with your new unique Pi ID.

4. **Reboot **  
   - Save your changes, reboot the Pi




Your new Pi is now ready to coordinate its sensor nodes!
Make sure the Pi is connected to a wifi (not needed for data collection) but just to ensure correct date and time

## Important Note

> ⚠️ **Do not deploy multiple clusters in close proximity.**  
> LoRa radio collisions between nearby clusters can lead to undefined behavior and garbage data readings.

## Flashing a Sensor Node

1. **Install Arduino IDE**  
   - Download and install from https://www.arduino.cc/en/software

2. **Add the RF95 LoRa Library**  
   - Open Arduino IDE  
   - Go to **Sketch > Include Library > Manage Libraries…**  
   - Search for **Adafruit RFM95** and install **Adafruit RFM95 LoRa Radio Library**

3. **Connect the Feather M0**  
   - Plug your Feather M0 RFM9x into your computer via USB

4. **Open the Firmware Sketch**  
   - In Arduino IDE, select **File > Open** and choose the `.ino` in `firmware/`

5. **Set the Device ID**  
   - Navigate to **Line 149**, find:
     ```c
     #define DEVICE_ID  1234 (can be a different number)
     ```
   - Replace `1234` with the unique integer ID for this node (must not duplicate any other device or Pi)

6. **Set the Coordinator (Pi) ID**  
   - Navigate to **Line 213**, find:
     ```c
     radiopacket[0] = 5678 (can be a different number);
     ```
   - Replace `5678` with the integer ID of the Raspberry Pi this node will talk to  
   - (Ensure the Pi is configured with this same ID in its `radio_communication_gui.py`)

7. **Flash the Node**  
   - In Arduino IDE’s **Tools > Port**, select your Feather’s port  
   - In **Tools > Board**, choose **Adafruit Feather M0**  
   - Click **Upload** (▶️)

Your sensor node is now flashed with its DEVICE_ID and Pi ID—ready to join the cluster!


## Functional Overview

- The Raspberry Pi continuously iterates over the `devices` list:  
  1. Sends a one-byte packet containing a device’s ID.  
  2. Waits for a set timeout period for a response.  
    - If a response is received, the Pi logs the data to `/home/pi/gasanalyzerdata`.  
    - If no response, the device is marked **offline**, and the Pi moves on.  

- Each Sensor Node:  
  1. Listens for incoming bytes.  
  2. When a byte matching its own `DEVICE_ID` arrives:  
     - Performs an ADC measurement.  
     - Sends the measurement packet back to the Pi over LoRa.  
     - Returns to listening for its next turn.
