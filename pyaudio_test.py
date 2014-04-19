#! /usr/bin/env python
# coding: utf-8

import pyaudio
import wave
import time


chunk = 256;
filename = "out.wav"
wf = wave.open(filename, "rb");
pa = pyaudio.PyAudio()

def callback(in_data, frame_count, time_info, status):
    data = wf.readframes(frame_count)
    return (data, pyaudio.paContinue)

stream = pa.open(format = pa.get_format_from_width(wf.getsampwidth()),
        channels = wf.getnchannels(),
        rate = wf.getframerate(),
        output = True,
        frames_per_buffer = chunk,
        stream_callback=callback)

stream.start_stream()

while stream.is_active():
    print stream.is_active()
    time.sleep(0.1)

stream.stop_stream()
stream.close()
pa.terminate()

