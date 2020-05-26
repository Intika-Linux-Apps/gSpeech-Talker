gSpeech : Google Text To Speech Gui
=========

gSpeech: a simple GUI for SVox Pico TTS

Capture:
========

<p align="center">
  <img width="650" src="https://raw.githubusercontent.com/Intika-Linux-Apps/gSpeech-Talker/master/files/captures/capture.png">
</p>

Installation instruction:
=========================

This application uses [nanotts](https://github.com/gmn/nanotts) and require it to be installed 

Dependency: 
- nanotts
- python (>=2.7) 
- python-gst1.0 (>=1.0) 
- python-gtk2 (>=2.24) 
- libttspico-utils (>= 1.0) 
- python-notify (>=0.1) 
- gstreamer1.0-plugins-base 
- gstreamer1.0-plugins-good 
- gstreamer1.0-pulseaudio

Optional dependency: 
- sox (sox is needed to speech text with more than 2^15 characters)

Install:
- Clone git repository `git clone https://github.com/lusum/gSpeech.git`
- Create .desktop launcher for gSpeech.sh

