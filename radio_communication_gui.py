#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import tkinter as tk
import os
from datetime import datetime
import sys
import logging
import busio
from digitalio import DigitalInOut
import board
import adafruit_ssd1306
import adafruit_rfm9x

# ------------------------------------------------------------------------------
# Logging setup
# ------------------------------------------------------------------------------
LOG_FILE = '/home/rpi/radio_gui.log'
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)
logging.info("=== Starting radio_communication_gui.py ===")

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------
BASE_DIR = os.path.expanduser('~/gasanalyzerdata')
os.makedirs(BASE_DIR, exist_ok=True)
logging.info(f"Data directory: {BASE_DIR}")

# OLED setup (128x32)
try:
    i2c = busio.I2C(board.SCL, board.SDA)
    reset_pin = DigitalInOut(board.D4)
    display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, reset=reset_pin)
    display.fill(0)
    display.show()
    logging.info("Initialized OLED display")
except Exception as e:
    logging.exception("Failed to initialize OLED")

# LoRa setup (915 MHz)
try:
    CS = DigitalInOut(board.CE1)
    RESET = DigitalInOut(board.D25)
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 915.0)
    rfm9x.tx_power = 23
    rfm9x.preamble_length = 8
    rfm9x.spreading_factor = 7
    rfm9x.signal_bandwidth = 500000
    logging.info("Initialized RFM9x LoRa radio")
except Exception as e:
    logging.exception("Failed to initialize LoRa radio")
    sys.exit(1)

devices = list(range(13))
values = [0] * 14
POLL_INTERVAL_MS = 500

# ------------------------------------------------------------------------------
# Tkinter GUI setup
# ------------------------------------------------------------------------------
root = tk.Tk()
root.title("Device Status")
labels = {}
for idx, device in enumerate(devices):
    lbl = tk.Label(
        root,
        text=f"Device {device}\nUnknown",
        width=12,
        height=3,
        relief="ridge",
        borderwidth=2
    )
    lbl.grid(row=idx // 4, column=idx % 4, padx=5, pady=5)
    labels[device] = lbl
logging.info("Initialized Tkinter GUI with device labels")

# ------------------------------------------------------------------------------
# Polling function
# ------------------------------------------------------------------------------
def poll_devices():
    logging.info("poll_devices() start")
    try:
        display.fill(0)
        display.show()
    except Exception as e:
        logging.exception("OLED clear failed")

    for device in devices:
        try:
            logging.info(f"Sending permission to device {device}")
            rfm9x.send(device.to_bytes(1, 'little'))
        except Exception as e:
            logging.exception(f"Failed to send to device {device}")
            labels[device].config(text=f"Device {device}\nError", bg="orange")
            continue

        try:
            packet = rfm9x.receive(timeout=0.5)
            if packet is None:
                logging.info(f"No packet from device {device}")
                labels[device].config(text=f"Device {device}\nOffline", bg="red")
            else:
                logging.info(f"Packet received from device {device}: {packet!r}")
                for i in range(0, 27, 2):
                    values[i // 2] = int.from_bytes(packet[i:i+2], 'little')
                if values[0] == 9876:
                    labels[device].config(text=f"Device {device}\nOnline", bg="green")
                    # OLED update
                    try:
                        display.fill(0)
                        pt1 = ' '.join(str(v) for v in values[1:9])
                        pt2 = ' '.join(str(v) for v in values[9:14])
                        display.text(f"RX {device}:", 0, 0, 1)
                        display.text(pt1, 25, 0, 1)
                        display.text(pt2, 25, 8, 1)
                        display.show()
                        logging.info(f"OLED updated for device {device}")
                    except Exception as e:
                        logging.exception("OLED write failed")

                    # send ACK
                    try:
                        rfm9x.send((9).to_bytes(1, 'little'))
                        logging.info(f"Sent ACK to device {device}")
                    except Exception as e:
                        logging.exception("Failed to send ACK")

                    # write CSV
                    now = datetime.now()
                    timestamp = now.strftime("%H:%M:%S")
                    fname = os.path.join(
                        BASE_DIR,
                        f"dev-{device}_{now:%m-%d-%Y}.csv"
                    )
                    try:
                        if not os.path.isfile(fname):
                            with open(fname, 'x') as f:
                                f.write(
                                    "Timestamp,mq-2,mq-3,mq-4,mq-5,"
                                    "mq-6,mq-7,mq-8,mq-9,"
                                    "mq-135,mq-136,mq-137,mq-138\n"
                                )
                                logging.info(f"Created new CSV {fname}")
                        with open(fname, 'a') as f:
                            line = timestamp + ',' + ','.join(
                                str(v) for v in values[1:14]
                            ) + '\n'
                            f.write(line)
                            logging.info(f"Wrote data to {fname}")
                    except Exception as e:
                        logging.exception(f"Failed file IO for {fname}")

        except Exception as e:
            logging.exception(f"Error communicating with device {device}")
            labels[device].config(text=f"Device {device}\nError", bg="orange")

    logging.info("poll_devices() end\n")
    root.after(POLL_INTERVAL_MS, poll_devices)

# kick off polling
root.after(1000, poll_devices)
logging.info("Entering Tkinter mainloop")
root.mainloop()
logging.info("Exited Tkinter mainloop")
