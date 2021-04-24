#!/usr/bin/env python3

import asyncio
from evdev import InputDevice, ecodes,list_devices, util
import signal, sys
import json
import requests
from hbmqtt.client import MQTTClient
from hbmqtt.mqtt.constants import QOS_1
import os
import logging




# load config from json
config = {}
with open("/data/options.json", 'r') as f:
       config = json.load(f)


logging.basicConfig(level=logging.DEBUG if ("debug" in config and config["debug"] == True) else logging.INFO)

logging.info("Searching for devices...")
devices = [InputDevice(path) for path in list_devices()]
for device in devices:
    logging.info("\t {} {}".format(device.path, device.name))
    device.close()

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
        logging.error("Device {} could not be found. Please check device list above".format(config["device"]))
        sys.exit(0)

    logging.info("Opening HID {}".format(config["device"]))
    dev = InputDevice(config["device"])
except Exception as error:
    logging.error(error)
    sys.exit(0)

dev.grab()
logging.info("HID connected")





async def listener(dev):
    try:
        logging.info("Connecting to MQTT {}".format(config["mqtt_connection_string"]))
        await C.connect(config["mqtt_connection_string"])
    except Exception as error:
        logging.error("Error: {}".format(error))
        sys.exit(0)
    logging.info("Connected !")

    async for token in wait_for_token(dev):
        await C.publish(config["mqtt_topic"], str.encode(token), qos=QOS_1)
        logging.info("Token: {}".format(token))


scancodes = {
    # Scancode: ASCIICode
    # https://stackoverflow.com/a/19757397
    0: None, 1: u'ESC', 2: u'1', 3: u'2', 4: u'3', 5: u'4', 6: u'5', 7: u'6', 8: u'7', 9: u'8',
    10: u'9', 11: u'0', 12: u'-', 13: u'=', 14: u'BKSP', 15: u'TAB', 16: u'q', 17: u'w', 18: u'e', 19: u'r',
    20: u't', 21: u'y', 22: u'u', 23: u'i', 24: u'o', 25: u'p', 26: u'[', 27: u']', 28: u'CRLF', 29: u'LCTRL',
    30: u'a', 31: u's', 32: u'd', 33: u'f', 34: u'g', 35: u'h', 36: u'j', 37: u'k', 38: u'l', 39: u';',
    40: u'"', 41: u'`', 42: u'LSHFT', 43: u'\\', 44: u'z', 45: u'x', 46: u'c', 47: u'v', 48: u'b', 49: u'n',
    50: u'm', 51: u',', 52: u'.', 53: u'/', 54: u'RSHFT', 56: u'LALT', 57: u' ', 100: u'RALT'
}



async def wait_for_token(dev):
    buffer=""
    async for event in dev.async_read_loop():
        parsed_event = util.categorize(event)
        logging.debug("USB Event: {}".format(repr(parsed_event)))

        if (event.type == ecodes.EV_KEY and event.value == 1):
            
            if parsed_event.scancode == 28: # enter was pressed
                yield buffer
                buffer=""
            elif parsed_event.scancode in scancodes:
                buffer += scancodes[parsed_event.scancode]
            else:
                logging.warning("Unknown scancode ({})".format(parsed_event))

            if len(buffer) > int(config["max_token_length"]): # protect buffer len
                buffer = ""
                logging.warning("MAX_TOKEN_LEN exceeded")
        else:
            logging.warning("Non keyboard usb event received")


loop = asyncio.get_event_loop()
loop.run_until_complete(listener(dev))
