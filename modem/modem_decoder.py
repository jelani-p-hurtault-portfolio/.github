# modem_decoder.py
# Decodes a secret message hidden in a WAV audio file.
# The audio is encoded using the Bell 103 modem protocol —
# basically the same "beep-boop" sounds old dial-up modems made.

import wave
import numpy as np

# ── What frequencies are we listening for? ──────────────────────────────────
# The modem uses two tones to talk. Think of it like Morse code, but with
# sound pitches instead of dots and dashes:
#   - A HIGH tone (2225 Hz) means the bit is a 1
#   - A LOW  tone (2025 Hz) means the bit is a 0
FREQ_MARK  = 2225   # "mark"  = 1 bit
FREQ_SPACE = 2025   # "space" = 0 bit

SAMPLE_RATE   = 48000   # The WAV file has 48,000 samples per second
BAUD_RATE     = 300     # 300 bits per second (very slow by modern standards!)
SAMPLES_PER_BIT  = SAMPLE_RATE // BAUD_RATE   # = 160 samples make up one bit
SAMPLES_PER_BYTE = SAMPLES_PER_BIT * 10       # = 1600 samples make up one byte
                                               #   (1 start + 8 data + 1 stop)


def load_wav(filename):
    """
    Open the WAV file and pull out the raw audio as floating-point numbers
    between -1.0 and +1.0.  We convert from the original 16-bit integers
    because floating point is easier to do math with and won't overflow.
    """
    with wave.open(filename, 'rb') as wf:
        n_frames = wf.getnframes()
        raw_bytes = wf.readframes(n_frames)

    # The file stores each sample as a 16-bit signed integer.
    samples_int = np.frombuffer(raw_bytes, dtype=np.int16)

    # Divide by 32768 to squish everything into the -1.0 … +1.0 range.
    samples_float = samples_int.astype(np.float64) / 32768.0

    return samples_float


def tone_power(samples, freq, sample_rate):
    """
    "How strongly does this chunk of audio match a sine wave at `freq` Hz?"

    This works by comparing the audio against a perfect reference sine (and
    cosine) at the target frequency.  If the audio really IS that frequency,
    the numbers line up and the result is large.  If it's the wrong frequency,
    everything cancels out and the result is small.

    Think of it like a tuning fork: tap it near a guitar string that's already
    vibrating at the same pitch and it rings loud; near the wrong pitch, nothing.

    Returns a single non-negative number — bigger means "yes, that frequency
    is in here".
    """
    n = len(samples)
    # Build the reference waves once (one cosine, one sine at `freq`)
    time_steps = np.arange(n)
    angle = 2 * np.pi * freq * time_steps / sample_rate

    # numpy.dot is just multiply-then-add-everything-up, which is fast
    I = np.dot(samples, np.cos(angle))   # "in-phase" component
    Q = np.dot(samples, np.sin(angle))   # "quadrature" component

    # Power = I² + Q².  We don't need the square root — we're only comparing
    # two numbers to see which one is bigger.
    return I**2 + Q**2


def decode_bit(chunk):
    """
    Given 160 audio samples that represent ONE bit, decide if it's a 0 or 1.
    Whichever frequency scores higher wins.
    """
    power_mark  = tone_power(chunk, FREQ_MARK,  SAMPLE_RATE)  # score for "1"
    power_space = tone_power(chunk, FREQ_SPACE, SAMPLE_RATE)  # score for "0"

    return 1 if power_mark > power_space else 0


def decode_byte(samples, byte_start):
    """
    Decode one full byte (character) from the audio.

    Each byte is packaged in a 10-bit "frame":
        bit 0       — start bit  (should always be 0, just says "here comes a byte!")
        bits 1–8    — the actual data, sent least-significant-bit first
        bit 9       — stop bit   (should always be 1, says "that's the end")

    We read all 10 bits, ignore the start and stop, then reassemble the 8
    data bits into a number (0–255) which maps to an ASCII character.
    """
    bits = []
    for bit_index in range(10):
        start = byte_start + bit_index * SAMPLES_PER_BIT
        chunk = samples[start : start + SAMPLES_PER_BIT]
        bits.append(decode_bit(chunk))

    # bits[0] is the start bit — skip it
    # bits[9] is the stop  bit — skip it
    data_bits = bits[1:9]   # the 8 bits we actually care about

    # The bits arrive least-significant-bit first, so bit[0] is worth 1,
    # bit[1] is worth 2, bit[2] is worth 4, and so on.
    value = 0
    for i, b in enumerate(data_bits):
        value += b * (2 ** i)   # e.g. bit 0 adds 1, bit 1 adds 2, bit 2 adds 4…

    return value   # a number like 72, which is 'H' in ASCII


def decode_message(filename):
    """
    Read the whole WAV file and decode every byte in it.
    Stops when it either runs out of audio or hits a null byte (value 0),
    which is the standard "end of string" marker.
    """
    print(f"Loading audio from: {filename}")
    samples = load_wav(filename)

    total_samples = len(samples)
    total_bytes   = total_samples // SAMPLES_PER_BYTE

    print(f"  Audio length : {total_samples} samples")
    print(f"  Bytes to read: {total_bytes}")
    print()

    message_chars = []

    for byte_num in range(total_bytes):
        byte_start = byte_num * SAMPLES_PER_BYTE

        # Make sure we have enough audio left for a full byte
        if byte_start + SAMPLES_PER_BYTE > total_samples:
            break

        char_value = decode_byte(samples, byte_start)

        # Value 0 means "end of message" — we're done
        if char_value == 0:
            break

        # Only keep printable ASCII characters (32–126) to avoid weird symbols
        if 32 <= char_value <= 126:
            message_chars.append(chr(char_value))
        else:
            # Non-printable byte — print a placeholder so we know it happened
            message_chars.append(f"[{char_value}]")

    message = "".join(message_chars)
    return message


# ── Run it! ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    input_file  = "message.wav"
    output_file = "MESSAGE.txt"

    decoded = decode_message(input_file)

    print("=" * 50)
    print("DECODED MESSAGE:")
    print("=" * 50)
    print(decoded)
    print("=" * 50)

    # Save the result so you can turn it in
    with open(output_file, "w") as f:
        f.write(decoded + "\n")

    print(f"\nMessage saved to {output_file}")