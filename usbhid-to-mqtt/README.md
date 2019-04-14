# USB HID to MQTT Addon

This addon processes tokens from card or barcode readers that use a virtual USB keyboard to type number codes followed by an "Enter" key.

## Configuration
Protection mode **must be disabled** as the addon connects directly to the usb device to gain exclusive access.

All input devices are added under `/dev/input/event{NUMBER}` and a good guess for the first external token reader is `event2`. 
You can either try different values or use the [SSH & Web Terminal](https://github.com/hassio-addons/addon-ssh) Community Addon to find the right device.

Use `mqtt://homeassistant` as `mqtt_connection_string` to use the homeassitant mqtt broker.
Supply a password with `mqtt://username:password@homeassistant`.

Make sure to set `max_token_length` to a reasonable length slightly exeeding the expected maximum length of tokens read from the device. 

## Supported Devices

The addon was tested with a Neuftech USB RFID Reader, but any USB keyboard device should work.

