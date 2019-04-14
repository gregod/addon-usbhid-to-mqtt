ARG BUILD_FROM=hassioaddons/base:3.0.1
# hadolint ignore=DL3006
FROM ${BUILD_FROM}



# Setup base
RUN  apk add --no-cache \
        libevdev-dev \
        linux-headers \
        build-base

# Copy Python requirements file
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt


RUN  apk del --no-cache --purge \
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
    org.label-schema.url="http://localhost" \
    org.label-schema.usage="http://localhost" \
    org.label-schema.vcs-ref=${BUILD_REF} \
    org.label-schema.vcs-url="http://localhost" \
    org.label-schema.vendor="Local Add-ons"
