# Use official Python image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y libglib2.0-0 libxkbcommon-x11-0 libxcb-xinerama0 libgl1 libegl1 libfontconfig1 libdbus-1.3 binutils && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pyinstaller

# Copy the rest of the application code
COPY . .

COPY build.sh ./
RUN chmod +x build.sh
CMD ["./build.sh"]
