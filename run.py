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
logging.info("HID connected")

if config["grab_device"]:
    dev.grab()
    logging.info("HID Grabbed")







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
    0: None, 1: 'ESC', 2: '1', 3: '2', 4: '3', 5: '4', 6: '5', 7: '6', 8: '7', 9: '8',
    10: '9', 11: '0', 12: '-', 13: '=', 14: 'BKSP', 15: 'TAB', 16: 'q', 17: 'w', 18: 'e', 19: 'r',
    20: 't', 21: 'y', 22: '', 23: 'i', 24: 'o', 25: 'p', 26: '[', 27: ']', 28: 'CRLF', 29: 'LCTRL',
    30: 'a', 31: 's', 32: 'd', 33: 'f', 34: 'g', 35: 'h', 36: 'j', 37: 'k', 38: 'l', 39: ';',
    40: '"', 41: '`', 42: 'LSHFT', 43: '\\', 44: 'z', 45: 'x', 46: 'c', 47: 'v', 48: 'b', 49: 'n',
    50: 'm', 51: ',', 52: '.', 53: '/', 54: 'RSHFT', 56: 'LALT', 57: ' ', 100: 'RALT',
    #keypad
    55 : '*', 74: '-', 78 : '+', 83 : '.' , 98 : '/',
    71 : '7', 72 : '8' , 73 : '9',
    75 : '4', 76 : '5', 77 : '6',
    79 : '1', 80 : '2', 81 : '3'




}

capscodes = {
    # Scancode: ASCIICode
    # https://stackoverflow.com/a/19757397
    0: None, 1: 'ESC', 2: '!', 3: '@', 4: '#', 5: '$', 6: '%', 7: '^', 8: '&', 9: '*',
    10: '(', 11: ')', 12: '_', 13: '+', 14: 'BKSP', 15: 'TAB', 16: 'Q', 17: 'W', 18: 'E', 19: 'R',
    20: 'T', 21: 'Y', 22: '', 23: 'I', 24: 'O', 25: 'P', 26: '{', 27: '}', 28: 'CRLF', 29: 'LCTRL',
    30: 'A', 31: 'S', 32: 'D', 33: 'F', 34: 'G', 35: 'H', 36: 'J', 37: 'K', 38: 'L', 39: ':',
    40: '\'', 41: '~', 42: 'LSHFT', 43: '|', 44: 'Z', 45: 'X', 46: 'C', 47: 'V', 48: 'B', 49: 'N',
    50: 'M', 51: '<', 52: '>', 53: '?', 54: 'RSHFT', 56: 'LALT',  57: ' ', 100: 'RALT',
    #keypad
    55 : '*', 74: '-', 78 : '+', 83 : '.', 98 : '/',
    71 : '7', 72 : '8' , 73 : '9',
    75 : '4', 76 : '5', 77 : '6',
    79 : '1', 80 : '2', 81 : '3'
}
async def wait_for_token(dev):

    caps = False
    buffer=""
    async for event in dev.async_read_loop():
        parsed_event = util.categorize(event)  
        logging.debug("USB Event: {}".format(repr(parsed_event)))
        if (event.type == ecodes.EV_KEY):  
            if parsed_event.scancode == 42:
                if parsed_event.keystate == 1:
                    caps = True
                if parsed_event.keystate == 0:
                    caps = False
            if parsed_event.keystate == 1:  # Down events only
                if parsed_event.scancode == 28 or parsed_event.scancode == 96: # Yield code on enter / keypad enter
                    yield buffer
                    buffer=""
                else:
                    if config["raw_scancodes"]: # add raw scancode to buffer
                        buffer += "{},".format(parsed_event.scancode)
                    else:
                        if parsed_event.scancode != 42:  # ignore shift, is handled in caps on/off mode
                            buffer += (capscodes if caps else scancodes).get(parsed_event.scancode,'KEY({})'.format(parsed_event.scancode))
                
                    

            if len(buffer) > int(config["max_token_length"]): # protect buffer len
                buffer = ""
                logging.warning("MAX_TOKEN_LEN exceeded")


loop = asyncio.get_event_loop()
loop.run_until_complete(listener(dev))
