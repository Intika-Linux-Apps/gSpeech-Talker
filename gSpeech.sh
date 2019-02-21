#!/bin/bash
gSpeech=`dirname "$(cd ${0%/*} && echo $PWD/${0##*/})"`
cd $gSpeech
python ./gSpeech.py
exit 0
