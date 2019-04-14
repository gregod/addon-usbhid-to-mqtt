#!/usr/bin/with-contenv python3
# ==============================================================================
#
# Community Hass.io Add-ons: Example
#
# Example add-on for Hass.io.
# This add-on displays a random quote every X seconds.
#
# ==============================================================================

import asyncio
from evdev import InputDevice, categorize, ecodes
import signal, sys
import json
import requests
import logging
from hbmqtt.client import MQTTClient
from hbmqtt.mqtt.constants import QOS_1, QOS_2
import os

logging.basicConfig(level=logging.INFO)

MAX_TOKEN_LEN = 10

# load config from json
config = {}
with open("/data/options.json", 'r') as f:
       config = json.load(f)

# handle program exit
def signal_handler(signal, frame):
    dev.ungrab()
    C.disconnect()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


C = MQTTClient()

# connect to usb input device
try:
    logging.info("Opening HID {}".format(config["device"]))
    dev = InputDevice(config["device"])
except Exception as error:
    logging.error("Error: ", error)
    sys.exit(0)

dev.grab()
logging.info("HID connected")





async def listener(dev):
    try:
        logging.info("Connecting to MQTT {}".format(config["mqtt_connection_string"]))
        await C.connect(config["mqtt_connection_string"])
    except Exception as error:
        logging.error("Error: ", error)
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

            if len(buffer) > MAX_TOKEN_LEN: # protect buffer len
                buffer = ""
                logging.error("Error: MAX_TOKEN_LEN exceeded")


loop = asyncio.get_event_loop()
loop.run_until_complete(listener(dev))
