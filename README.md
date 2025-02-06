# Project Overview

This repository contains the necessary scripts for Raspberry Pi and Arduino to facilitate LoRa communication and data collection. The system is designed to collect data from multiple nodes, store it locally, and upload it to an Azure SQL database. Some additional setup is required to enable database storage functionality.

## Raspberry Pi

The `pi` folder contains Python scripts that manage communication, data collection, and display functionalities. Below is an overview of the key scripts:

### Key Scripts

- **`wifi_display.py`**: Displays the IP address of the Raspberry Pi upon boot. This is useful for SSH access.
- **`single_device_lora.py`**: Manages LoRa communication with a single node.
- **`multidevice_lora.py`**: Handles LoRa communication with multiple nodes. Node IDs and the number of nodes must be manually configured.
- **`raspi-blinka.py`**: Installs Blinka, a dependency required for running CircuitPython libraries. For more information, visit:
  - [CircuitPython](https://circuitpython.org/)
  - [Running CircuitPython Code on Raspberry Pi](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/running-circuitpython-code-without-circuitpython)
- **Testing Scripts (`test-db` and others)**: Various test scripts that may no longer function as expected.

### Database Integration

The Raspberry Pi is intended to upload collected data to an Azure SQL database while also storing it locally. Additional configuration is required to establish the database connection and ensure data is uploaded correctly.

## Arduino

The Arduino firmware is responsible for reading ADC values and transmitting data over UART. The following considerations must be taken into account:

- The **node ID** must be hardcoded in the sketch before flashing.
- Each device must have a unique ID to avoid conflicts.
- Reflashing a device requires careful ID management to prevent duplication.

## Setup & Configuration

### Raspberry Pi

1. Install necessary dependencies, including CircuitPython and Blinka.
2. Configure LoRa settings in `single_device_lora.py` or `multidevice_lora.py`.
3. Ensure database connectivity settings are correctly set up for Azure SQL.

### Arduino

1. Modify the sketch to set the correct node ID before flashing.
2. Flash the firmware onto each Arduino device, ensuring unique IDs for all nodes.


