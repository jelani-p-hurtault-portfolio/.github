"""
Jelani Hurtault
CS 516
Assignment # 1 Clipped
"""

import numpy as np           # Math library
from scipy.io import wavfile # Library for reading and writing WAV files
import sounddevice as sd     # Library needed to interface with host audio hardware

# --- Audio Parameters ---
SAMPLE_RATE = 48000       # samples per second to represent sound waves digitally
DURATION = 1.0            # I only want it to last 1 second in length
FREQUENCY = 440           # The concert A tuning reference in Hz 
MAX_AMP = 32767           # max 16-bit signed amplitude

QUARTER_AMP = MAX_AMP // 4   # used for sine.wav and clip threshold
HALF_AMP = MAX_AMP // 2      # used as base for clipped.wav


def generate_sine(amplitude: int) -> np.ndarray:
    """Generate one second of a 440Hz sine wave at the given amplitude."""
    t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), endpoint=False)
    samples = amplitude * np.sin(2 * np.pi * FREQUENCY * t)
    return samples.astype(np.int16)


def generate_clipped_sine() -> np.ndarray:
    """Generate a ½-amplitude sine wave hard-clipped at ¼ amplitude."""
    t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), endpoint=False)
    samples = HALF_AMP * np.sin(2 * np.pi * FREQUENCY * t)
    # Hard clip: clamp values to [-QUARTER_AMP, QUARTER_AMP]
    clipped = np.clip(samples, -QUARTER_AMP, QUARTER_AMP)
    return clipped.astype(np.int16)


def write_wav(filename: str, samples: np.ndarray) -> None:
    """Write samples to a WAV file at SAMPLE_RATE."""
    wavfile.write(filename, SAMPLE_RATE, samples)
    print(f"  Written: {filename}  ({len(samples)} samples, {SAMPLE_RATE}Hz, 16-bit mono)")


def play_samples(samples: np.ndarray) -> None:
    """Play 16-bit integer samples directly via sounddevice (no file I/O)."""
    # sounddevice expects float32 in [-1.0, 1.0]
    float_samples = samples.astype(np.float32) / MAX_AMP
    print(f"  Playing {DURATION}s clipped sine wave at {FREQUENCY}Hz ...")
    sd.play(float_samples, samplerate=SAMPLE_RATE)
    sd.wait()   # block until playback finishes
    print("  Playback complete.")


def main():
    print("=== Part 1: Generate sine.wav (¼ amplitude, 440Hz) ===")
    sine_samples = generate_sine(QUARTER_AMP)
    write_wav("sine.wav", sine_samples)

    print("\n=== Part 2: Generate clipped.wav (½ amplitude clipped at ¼) ===")
    clipped_samples = generate_clipped_sine()
    write_wav("clipped.wav", clipped_samples)

    print("\n=== Part 3: Play clipped sine wave directly to audio output ===")
    play_samples(clipped_samples)

    print("\nDone.")


if __name__ == "__main__":
    main()