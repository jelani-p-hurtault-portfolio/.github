# Jelani Hurtault

## Synth

A real-time MIDI synthesizer written in Python using sounddevice and mido.

### What I Did

Built a soft synthesizer that listens for MIDI input and plays audio in real time.
The synth supports multiple waveforms, polyphony, velocity sensitivity, an ADSR
envelope, and an optional noise layer.

### Features

- Sawtooth wave synthesis (default)
- Sine, square, and triangle waveforms via flags
- AR envelope with 10ms attack and release
- ADSR envelope with decay and sustain
- Polyphony (multiple notes at once)
- MIDI key on velocity controls note volume
- MIDI key off velocity controls release time
- Optional white noise layer with --noise
- Direct MIDI device selection with --midi-device

### How to Run

Install dependencies:

    pip install mido python-rtmidi sounddevice numpy

Run the synth:

    python synth.py

With options:

    python synth.py --sine
    python synth.py --square
    python synth.py --triangle
    python synth.py --noise
    python synth.py --midi-device "IAC Driver"

### What Is Still To Be Done

- MIDI CC message support (pitch bend, modulation)
- Reverb or delay effects
- GUI interface