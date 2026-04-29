# Modem Decoder
by Jelani Hurtault

So basically this project decodes a secret message hidden inside an audio file.
The audio is just a recording of old dial-up modem sounds from the 80s — you 
know, that awful screeching noise your parents' internet used to make.

The way it works is pretty cool actually. The modem uses two different sound 
frequencies to represent 1s and 0s. High pitch = 1, lower pitch = 0. The code 
listens to tiny chunks of audio at a time and figures out which tone it is, 
then builds that into letters and words.

## What it does
- Reads a WAV audio file
- Detects the tones and converts them to bits
- Turns those bits into actual readable text
- Saves the decoded message to a text file

## How to run it
Make sure you have Python and numpy installed, then just: