import numpy as np
import sounddevice as sd

SAMPLE_RATE = 48000
AMPLITUDE = 0.708
ATTACK_MS = 10
RELEASE_MS = 10

def midi_to_freq(midi_note):
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))

def apply_envelope(audio, attack_ms, release_ms):
    attack_samples = int(SAMPLE_RATE * attack_ms / 1000)
    release_samples = int(SAMPLE_RATE * release_ms / 1000)
    total = len(audio)

    envelope = np.ones(total, dtype=np.float32)

    attack_samples = min(attack_samples, total)
    envelope[:attack_samples] = np.linspace(0.0, 1.0, attack_samples)

    release_samples = min(release_samples, total - attack_samples)
    envelope[total - release_samples:] = np.linspace(1.0, 0.0, release_samples)

    return audio * envelope

def sawtooth_wave(freq, duration):
    num_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    wave = 2.0 * (t * freq - np.floor(t * freq + 0.5))
    return (wave * AMPLITUDE).astype(np.float32)

freq = midi_to_freq(60)
audio = sawtooth_wave(freq, 1.0)
audio = apply_envelope(audio, ATTACK_MS, RELEASE_MS)

sd.play(audio, SAMPLE_RATE)
sd.wait()
print("Done.")