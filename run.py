#!/usr/bin/env python3

import asyncio
from evdev import InputDevice, ecodes,list_devices
import signal, sys
import json
import requests
from hbmqtt.client import MQTTClient
from hbmqtt.mqtt.constants import QOS_1
import os
import logging
logging.basicConfig(level=logging.INFO)

logging.info("Searching for devices...")
devices = [InputDevice(path) for path in list_devices()]
for device in devices:
    logging.info("\t {} {}".format(device.path, device.name))
    device.close()

# load config from json
config = {}
with open("/data/options.json", 'r') as f:
       config = json.load(f)

# handle program exit
def signal_handler(signal, frame):
    try:
        dev.ungrab()
    except:
        pass
    try:
        C.disconnect()
    except:
        pass
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


C = MQTTClient()

# connect to usb input device
try:

    if config["device"] not in list_devices():
        logging.error("Error: Device {} could not be found. Please check device list above".format(config["device"]))
        sys.exit(0)

    logging.info("Opening HID {}".format(config["device"]))
    dev = InputDevice(config["device"])
except Exception as error:
    logging.error("Error: {}".format(error))
    sys.exit(0)

dev.grab()
logging.info("HID connected")





async def listener(dev):
    try:
        logging.info("Connecting to MQTT {}".format(config["mqtt_connection_string"]))
        await C.connect(config["mqtt_connection_string"])
    except Exception as error:
        logging.info("Error: {}".format(error))
        sys.exit(0)
    logging.info("Connected !")

    async for token in wait_for_token(dev):
        await C.publish(config["mqtt_topic"], str.encode(token), qos=QOS_1)
        logging.info("Token: {}".format(token))


async def wait_for_token(dev):
    buffer=""
    async for event in dev.async_read_loop():
         if (event.type == ecodes.EV_KEY and event.value == 1):
            if event.code == 28: # enter was pressed
                yield buffer
                buffer=""
            elif event.code >= 2 and event.code <= 10: # keys 1-9
                buffer += str(event.code - 1)
            elif event.code == 11: # key 0
                buffer += "0"

            if len(buffer) > int(config["max_token_length"]): # protect buffer len
                buffer = ""
                logging.warning("Warning: MAX_TOKEN_LEN exceeded")


loop = asyncio.get_event_loop()
loop.run_until_complete(listener(dev))
