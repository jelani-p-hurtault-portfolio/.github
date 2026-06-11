import numpy as np
import sounddevice as sd
import mido
import threading
import argparse

SAMPLE_RATE = 48000
AMPLITUDE = 0.708
BLOCK_SIZE = 256

ATTACK_MS = 10
DECAY_MS = 50
SUSTAIN_LEVEL = 0.7
RELEASE_MS = 10

attack_samples = int(SAMPLE_RATE * ATTACK_MS / 1000)
decay_samples = int(SAMPLE_RATE * DECAY_MS / 1000)
release_samples = int(SAMPLE_RATE * RELEASE_MS / 1000)

lock = threading.Lock()
waveform = "sawtooth"
add_noise = False
voices = {}

def midi_to_freq(midi_note):
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))

def get_sample(phase, waveform):
    if waveform == "sine":
        return np.sin(2.0 * np.pi * phase)
    elif waveform == "square":
        return 1.0 if phase < 0.5 else -1.0
    elif waveform == "triangle":
        return 4.0 * abs(phase - 0.5) - 1.0
    else:
        return 2.0 * (phase - np.floor(phase + 0.5))

def get_envelope_amp(v):
    pos = v["env_pos"]

    if v["releasing"]:
        progress = pos / max(release_samples, 1)
        amp = v["release_amp"] * (1.0 - progress)
        return max(amp, 0.0), pos >= release_samples

    if pos < attack_samples:
        return pos / max(attack_samples, 1), False

    pos2 = pos - attack_samples
    if pos2 < decay_samples:
        amp = 1.0 - (1.0 - SUSTAIN_LEVEL) * (pos2 / max(decay_samples, 1))
        return amp, False

    return SUSTAIN_LEVEL, False

def audio_callback(outdata, frames, time, status):
    global voices, add_noise

    output = np.zeros(frames, dtype=np.float32)

    with lock:
        finished = []
        for note, v in voices.items():
            for i in range(frames):
                sample = get_sample(v["phase"], waveform)

                if add_noise:
                    sample += np.random.uniform(-0.1, 0.1)

                amp, done = get_envelope_amp(v)

                if done:
                    finished.append(note)
                    break

                v["current_amp"] = amp
                v["env_pos"] += 1

                output[i] += sample * amp * v["velocity"] * AMPLITUDE
                v["phase"] += v["freq"] / SAMPLE_RATE
                v["phase"] -= np.floor(v["phase"])

        for note in finished:
            del voices[note]

    output = np.clip(output, -1.0, 1.0)
    outdata[:, 0] = output

def note_start(midi_note, velocity):
    with lock:
        voices[midi_note] = {
            "freq": midi_to_freq(midi_note),
            "phase": 0.0,
            "env_pos": 0,
            "releasing": False,
            "release_amp": 0.0,
            "current_amp": 0.0,
            "velocity": velocity / 127.0,
        }

def note_stop(midi_note, velocity=64):
    global release_samples
    with lock:
        if midi_note in voices:
            release_ms = 10 + (127 - velocity) * 2
            release_samples = int(SAMPLE_RATE * release_ms / 1000)
            voices[midi_note]["releasing"] = True
            voices[midi_note]["release_amp"] = voices[midi_note]["current_amp"]
            voices[midi_note]["env_pos"] = 0

parser = argparse.ArgumentParser()
parser.add_argument("--midi-device", type=str, default=None)
parser.add_argument("--sine", action="store_true")
parser.add_argument("--square", action="store_true")
parser.add_argument("--triangle", action="store_true")
parser.add_argument("--noise", action="store_true")
args = parser.parse_args()

if args.sine:
    waveform = "sine"
elif args.square:
    waveform = "square"
elif args.triangle:
    waveform = "triangle"
else:
    waveform = "sawtooth"

add_noise = args.noise

print(f"Waveform: {waveform}")
print(f"Noise: {add_noise}")

ports = mido.get_input_names()
if not ports:
    print("No MIDI ports found.")
    exit()

if args.midi_device:
    matches = [p for p in ports if args.midi_device.lower() in p.lower()]
    port_name = matches[0] if matches else ports[0]
else:
    port_name = ports[0]

print(f"Listening on: {port_name}")
print("Ready. Press keys on your MIDI keyboard.")

with sd.OutputStream(samplerate=SAMPLE_RATE, channels=1,
                     blocksize=BLOCK_SIZE, callback=audio_callback):
    with mido.open_input(port_name) as port:
        for msg in port:
            if msg.type == "note_on" and msg.velocity > 0:
                note_start(msg.note, msg.velocity)
            elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                note_stop(msg.note, msg.velocity)