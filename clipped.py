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


"""
References

Libraries — Official Documentation
- NumPy: https://numpy.org/doc/stable/
- NumPy linspace: https://numpy.org/doc/stable/reference/generated/numpy.linspace.html
- NumPy sin: https://numpy.org/doc/stable/reference/generated/numpy.sin.html
- NumPy clip: https://numpy.org/doc/stable/reference/generated/numpy.clip.html
- SciPy wavfile.write: https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.wavfile.write.html
- sounddevice: https://python-sounddevice.readthedocs.io/en/latest/

Audio & Signal Processing Concepts
- WAV file format: https://en.wikipedia.org/wiki/WAV
- Sine wave: https://en.wikipedia.org/wiki/Sine_wave
- Hard clipping / fuzz effect: https://en.wikipedia.org/wiki/Clipping_(audio)
- Digital audio sampling: https://en.wikipedia.org/wiki/Sampling_(signal_processing)
- 16-bit audio / PCM: https://en.wikipedia.org/wiki/Pulse-code_modulation

Python Language References
- f-strings: https://docs.python.org/3/tutorial/inputoutput.html#formatted-string-literals
- Type hints: https://docs.python.org/3/library/typing.html
- if __name__ == "__main__": https://docs.python.org/3/reference/__main__.html
- Integer division //: https://docs.python.org/3/reference/expressions.html#binary-arithmetic-operations
"""