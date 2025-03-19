FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    # X11 / VNC
    xvfb x11vnc xauth x11-xserver-utils \
    x11-apps sudo software-properties-common \
    # Basic GUI automation
    xdotool \
    # Python & pip
    python3 python3-pip \
    # xfce4 desktop environment and goodies
    xfce4 xfce4-goodies \
    # D-Bus session launcher
    dbus-x11 \
    # Misc utilities
    curl wget git nano xterm \
    # Screenshot utilities
    imagemagick \
    # Remove unneeded dependencies and clean up
    && apt-get remove -y light-locker xfce4-screensaver xfce4-power-manager || true \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install firefox
RUN add-apt-repository ppa:mozillateam/ppa  && apt-get update  && apt-get install -y --no-install-recommends firefox-esr  && update-alternatives --set x-www-browser /usr/bin/firefox-esr  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Disable caret blink in firefox
USER root
RUN echo 'pref("ui.caretBlinkTime", 0);' > /usr/lib/firefox-esr/defaults/pref/local-settings.js

# Install/upgrade pip
RUN pip3 install --upgrade pip

# Create non-root user and set that as the working directory
RUN useradd -ms /bin/bash myuser     && echo "myuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
USER myuser
WORKDIR /home/myuser

# Set VNC password to ("secret")
RUN x11vnc -storepasswd secret /home/myuser/.vncpass

EXPOSE 5900

CMD Xvfb :99 -screen 0 1280x720x24 & \
    export DISPLAY=:99 && \
    # Start XFCE4 session
    startxfce4 & \
    # Start x11vnc with no password (local usage only)
    x11vnc -display :99 -N -forever -shared -rfbauth /home/myuser/.vncpass -rfbport 5900 & \
    # Keep container alive
    tail -f /dev/null
