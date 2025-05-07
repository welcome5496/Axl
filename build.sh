#!/bin/bash

# Install ffmpeg (static binary)
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz | tar xJ
mv ffmpeg-*-static/ffmpeg /usr/local/bin/
mv ffmpeg-*-static/ffprobe /usr/local/bin/

# Install Python dependencies
pip install -r requirements.txt
