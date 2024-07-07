#!/usr/bin/env python3
"""
Recognize live speech from the default audio device.
"""

# MIT license (c) 2022, see LICENSE for more information.
# Author: David Huggins-Daines <dhdaines@gmail.com>

from pocketsphinx import Endpointer, Decoder, set_loglevel
# import pyttsx3
import subprocess
import sys


def main():
    # pyttsx3 Setup
    # engine = pyttsx3.init()

    # List available voices
    # voices = engine.getProperty('voices')

    # print(f"ID: {voice.id} - Name: {voice.name}")

    # Set a specific voice
    # engine.setProperty('voice', voices[1].id)  # Choose a different index for different voices

    # engine.runAndWait()

    # PocketSphinx Setup
    set_loglevel("INFO")
    ep = Endpointer()
    decoder = Decoder(
        hmm="./models/acoustic/",
        lm="./models/language/en-70k-0.2.lm",
        dict="./models/dictionary/cmudict-en-us.dict",
        loglevel="INFO",
        samprate=ep.sample_rate,
    )
    soxcmd = f"sox -q -r {ep.sample_rate} -c 1 -b 16 -e signed-integer -d -t raw -"
    sox = subprocess.Popen(soxcmd.split(), stdout=subprocess.PIPE)
    while True:
        frame = sox.stdout.read(ep.frame_bytes)
        prev_in_speech = ep.in_speech
        speech = ep.process(frame)
        if speech is not None:
            if not prev_in_speech:
                print("Speech start at %.2f" % (ep.speech_start), file=sys.stderr)
                decoder.start_utt()
            decoder.process_raw(speech)
            hyp = decoder.hyp()
            if hyp is not None:
                print("PARTIAL RESULT:", hyp.hypstr, file=sys.stderr)
            if not ep.in_speech:
                print("Speech end at %.2f" % (ep.speech_end), file=sys.stderr)
                decoder.end_utt()
                print(decoder.hyp().hypstr)


try:
    main()
except KeyboardInterrupt:
    pass
