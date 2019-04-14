ARG BUILD_FROM=hassioaddons/base:3.0.1
# hadolint ignore=DL3006
FROM ${BUILD_FROM}


# Copy Python requirements file
COPY requirements.txt /tmp/


RUN  apk add --no-cache \
        libevdev-dev \
        linux-headers \
        build-base \
     && pip3 install --no-cache-dir -r /tmp/requirements.txt \
     && apk del --no-cache --purge \
        linux-headers \
        build-base



# Copy root filesystem
COPY rootfs /

# Script to run after startup
CMD ["/usr/bin/run.py"]

# Build arguments
ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_REF
ARG BUILD_VERSION

# Labels
LABEL \
    io.hass.name="USB HID Reader" \
    io.hass.description="Read Tokens from USB HID and publish them to a MQTT topic" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    maintainer="Gregor Godbersen <homeassistant@k9z.de>" \
    org.label-schema.description="Read Tokens from USB HID and publish them to a MQTT topic" \
    org.label-schema.build-date=${BUILD_DATE} \
    org.label-schema.name="USB HID Reader" \
    org.label-schema.schema-version="1.0" \
    org.label-schema.url="https://github.com/gregod/addon-usbhid-to-mqtt/tree/master/usbhid-to-mqtt" \
    org.label-schema.usage="https://github.com/gregod/addon-usbhid-to-mqtt/blob/master/usbhid-to-mqtt/README.md" \
    org.label-schema.vcs-ref=${BUILD_REF} \
    org.label-schema.vcs-url="https://github.com/gregod/addon-usbhid-to-mqtt/" \
    org.label-schema.vendor="Gregor Godbersen"
