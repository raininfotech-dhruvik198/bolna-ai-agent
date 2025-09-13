# Use a base image with build tools
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    cmake \
    wget

# Clone whisper.cpp
RUN git clone https://github.com/ggerganov/whisper.cpp.git /opt/whisper.cpp

# Build the server
WORKDIR /opt/whisper.cpp
RUN cmake -B build
RUN cmake --build build -j --config Release

# Download a model
RUN bash ./models/download-ggml-model.sh base.en

# Expose the server port
EXPOSE 9090

# Command to run the server
CMD ["./build/bin/server", "-m", "models/ggml-base.en.bin", "-t", "8", "--host", "0.0.0.0", "--port", "9090"]
