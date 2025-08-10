# Use official Python image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    libglib2.0-0 \
    libxkbcommon-x11-0 \
    libxcb-xinerama0 \
    libgl1 \
    libegl1 \
    libfontconfig1 \
    libdbus-1-3 \
    binutils \
    libxcb-render-util0 \
    libxcb-keysyms1 \
    libxcb-render0 \
    libxcb-icccm4 \
    libxcb-shape0 \
    libxcb-cursor0 \
    libxcb-image0 \
    libpango-1.0-0 \
    libatk1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libpangocairo-1.0-0 \
    libcairo-gobject2 \
    libgtk-3-0 \
    libcairo2 \
    libatomic1 && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pyinstaller

# Copy the rest of the application code
COPY . .

COPY build.sh ./
CMD ["./build.sh"]
