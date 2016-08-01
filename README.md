gSpeech
=======

gSpeech: a simple GUI for SVox Pico TTS


Installation instruction:
=========================

Ubuntu:

Depends: python (>=2.7) python-gst0.10 (>=0.10) python-gtk2 (>=2.24) libttspico-utils (>= 1.0) python-notify (>=0.1) gstreamer0.10-plugins-base gstreamer0.10-plugins-good gstreamer0.10-pulseaudio

Suggests: python-appindicator sox


In any directory, where you want to install

1) Clone git repository

git clone https://github.com/tuxmouraille/gSpeech.git

2) Create .desktop launcher for gSpeech.sh

3) Use it


NB:
- python-appindicator is used for a best integration with Ubuntu
- sox is needed to speech text with more than 2^15 characters
