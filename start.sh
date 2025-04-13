#!/bin/bash

# Download static ffmpeg build (latest)
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o ffmpeg.tar.xz
tar -xf ffmpeg.tar.xz
export PATH=$PATH:$(pwd)/ffmpeg-*/ # make ffmpeg available

# Run the bot
python3 main.py
