FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libegl1 libxkbcommon0 libxkbcommon-x11-0 libdbus-1-3 libfontconfig1 libglib2.0-0 \
    libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 \
    libxcb-render-util0 libxcb-xinerama0 libxcb-xfixes0 libxcb-cursor0 \
    x11-utils xauth tigervnc-standalone-server fluxbox novnc websockify \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY start-vnc.sh /start-vnc.sh
COPY docker/novnc-index.html /usr/share/novnc/index.html
RUN chmod +x /start-vnc.sh

VOLUME ["/app/data"]

CMD ["/start-vnc.sh"]
