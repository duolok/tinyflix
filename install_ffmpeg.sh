#!/bin/bash

FFMPEG_URL="https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
DEST_DIR="tinyflix-back/src/transcoder-layer"
BIN_DIR="$DEST_DIR/bin"
LAYER_VERSION_DIR="$DEST_DIR/layer_version"
LAYER_VERSION_BIN_DIR="$LAYER_VERSION_DIR/bin"

mkdir -p $BIN_DIR
mkdir -p $LAYER_VERSION_BIN_DIR

echo "Downloading ffmpeg..."
wget -O /tmp/ffmpeg.tar.xz $FFMPEG_URL

echo "Extracting ffmpeg..."
tar -xf /tmp/ffmpeg.tar.xz -C /tmp

FFMPEG_EXTRACTED_DIR=$(find /tmp -type d -name "ffmpeg-*")

echo "Copying ffmpeg binary..."
cp $FFMPEG_EXTRACTED_DIR/ffmpeg $BIN_DIR
cp $FFMPEG_EXTRACTED_DIR/ffmpeg $LAYER_VERSION_BIN_DIR

echo "Cleaning up..."
rm -rf /tmp/ffmpeg*
rm /tmp/ffmpeg.tar.xz

echo "ffmpeg installation completed successfully!"
