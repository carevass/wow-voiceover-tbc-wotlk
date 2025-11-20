# Use NVIDIA CUDA base image
ARG BASE=nvidia/cuda:11.8.0-base-ubuntu22.04
FROM ${BASE}

# Set working directory to /app to match your mounting strategy
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    git \
    wget \
    ffmpeg \
    espeak-ng \
    libsndfile1-dev \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv \
    python3-wheel \
    mysql-client \
    && rm -rf /var/lib/apt/lists/*

#Need SoX in the container for sfx with certain voices
RUN apt-get update && apt-get install -y sox libsox-fmt-all
ENV PATH="/usr/bin/sox:${PATH}"

# Clone RVC WebUI
WORKDIR /app

RUN pip3 install --upgrade pip==23.3.1 setuptools wheel

RUN pip3 install numpy==1.26.4 faiss-gpu==1.7.2

# Install fairseq first with pinned omegaconf
RUN pip3 install omegaconf==2.0.6 hydra-core==1.0.7


# Fix missing 'past' module for ffmpeg-python
RUN pip3 install future

# Pre-install workaround for llvmlite
RUN pip3 install llvmlite --ignore-installed

# Install PyTorch with CUDA 11.8 support
RUN pip3 install -v --no-cache-dir torch torchaudio --extra-index-url https://download.pytorch.org/whl/cu118

# Copy entire project root
COPY . /app


RUN pip3 install -r requirements.txt

# Expose API port
EXPOSE 7280

# Accept Coqui license
ENV COQUI_TOS_AGREED=1

# RVC expects this env var for weight loading
ENV weight_root=/app
ENV index_root=/app/fine_tuned/_rvc/indices

CMD ["python3", "infer-web.py", "--port", "7280"]

