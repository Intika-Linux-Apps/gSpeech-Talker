#!/bin/bash
here=`dirname "$(cd ${0%/*} && echo $PWD/${0##*/})"`
cd $here
python ./gSpeech.py
exit 0
