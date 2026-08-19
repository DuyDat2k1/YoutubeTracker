FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libegl1 libxkbcommon0 libdbus-1-3 libfontconfig1 \
    libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 \
    libxcb-render-util0 libxcb-xinerama0 libxcb-xfixes0 x11-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

VOLUME ["/app/data"]

CMD ["python", "-m", "app.main"]
