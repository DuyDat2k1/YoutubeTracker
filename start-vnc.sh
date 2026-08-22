#!/bin/bash
# Cross-platform entrypoint: runs the app inside a virtual display and
# exposes it via noVNC in the browser (http://localhost:6080).
# Works identically on Linux, Windows and macOS - no host X11 needed.

export HOME=/root
rm -rf /root/.vnc
mkdir -p /root/.config/tigervnc
printf 'password' | vncpasswd -f > /root/.config/tigervnc/passwd
chmod 600 /root/.config/tigervnc/passwd

# Virtual display, reachable only from inside the container
vncserver :1 -geometry 1600x1000 -depth 24 -SecurityTypes None -localhost yes || true

# Browser access -> VNC display
websockify --web=/usr/share/novnc 6080 localhost:5901 &

export DISPLAY=:1

# App in foreground
python -m app.main

vncserver -kill :1 || true
