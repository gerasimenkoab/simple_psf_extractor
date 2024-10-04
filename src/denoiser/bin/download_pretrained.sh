#!/bin/bash

function gdrive_download () {
  CONFIRM=$(curl -sc /tmp/cookies.txt "https://docs.google.com/uc?export=download&id=$1" | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')
  curl -Lb /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$CONFIRM&id=$1" -o $2
  rm -rf /tmp/cookies.txt
}

GDRIVE_ID=1kHJUqb-e7BARb63741DVdpg-WqCdG3z6
TAR_FILE=./experiments/pretrained.tar

mkdir -p ./experiments

gdrive_download $GDRIVE_ID $TAR_FILE
tar -xvf $TAR_FILE -C ./experiments/
rm $TAR_FILE
