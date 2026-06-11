import numpy as np
import sounddevice as sd

SAMPLE_RATE = 48000
AMPLITUDE = 0.708

def midi_to_freq(midi_note):
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))

def sawtooth_wave(freq, duration):
    num_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    wave = 2.0 * (t * freq - np.floor(t * freq + 0.5))
    return (wave * AMPLITUDE).astype(np.float32)

freq = midi_to_freq(60)
audio = sawtooth_wave(freq, 1.0)

sd.play(audio, SAMPLE_RATE)
sd.wait()
print("Done.")