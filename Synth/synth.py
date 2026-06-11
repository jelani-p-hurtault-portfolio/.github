import numpy as np
import sounddevice as sd
import mido
import threading

SAMPLE_RATE = 48000
AMPLITUDE = 0.708
ATTACK_MS = 10
RELEASE_MS = 10
BLOCK_SIZE = 256

audio_buffer = np.zeros(BLOCK_SIZE * 4, dtype=np.float32)
current_freq = None
note_on = False
phase = 0.0
attack_samples = int(SAMPLE_RATE * ATTACK_MS / 1000)
release_samples = int(SAMPLE_RATE * RELEASE_MS / 1000)
envelope_pos = 0
releasing = False
release_start_amp = 0.0
current_amp = 0.0
lock = threading.Lock()

def midi_to_freq(midi_note):
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))

def audio_callback(outdata, frames, time, status):
    global phase, envelope_pos, releasing, current_amp, release_start_amp, note_on, current_freq

    output = np.zeros(frames, dtype=np.float32)

    with lock:
        freq = current_freq
        is_on = note_on
        is_releasing = releasing

    if freq is None:
        outdata[:] = 0
        return

    for i in range(frames):
        sample = 2.0 * (phase - np.floor(phase + 0.5))

        with lock:
            if not releasing and note_on:
                if envelope_pos < attack_samples:
                    amp = envelope_pos / max(attack_samples, 1)
                    envelope_pos += 1
                else:
                    amp = 1.0
            elif releasing:
                progress = (envelope_pos) / max(release_samples, 1)
                amp = release_start_amp * (1.0 - progress)
                amp = max(amp, 0.0)
                envelope_pos += 1
                if envelope_pos >= release_samples:
                    current_freq = None
                    releasing = False
                    note_on = False
                    amp = 0.0
            else:
                amp = 0.0

            current_amp = amp

        output[i] = sample * amp * AMPLITUDE
        if freq:
            phase += freq / SAMPLE_RATE
            phase -= np.floor(phase)

    outdata[:, 0] = output

def note_start(midi_note):
    global current_freq, note_on, envelope_pos, releasing, phase
    with lock:
        current_freq = midi_to_freq(midi_note)
        note_on = True
        releasing = False
        envelope_pos = 0
        phase = 0.0

def note_stop():
    global releasing, envelope_pos, release_start_amp
    with lock:
        releasing = True
        envelope_pos = 0
        release_start_amp = current_amp

ports = mido.get_input_names()
if not ports:
    print("No MIDI ports found.")
    exit()

port_name = ports[0]
print(f"Listening on: {port_name}")

with sd.OutputStream(samplerate=SAMPLE_RATE, channels=1,
                     blocksize=BLOCK_SIZE, callback=audio_callback):
    with mido.open_input(port_name) as port:
        for msg in port:
            if msg.type == "note_on" and msg.velocity > 0:
                print(f"Note ON: {msg.note}")
                note_start(msg.note)
            elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                print(f"Note OFF: {msg.note}")
                note_stop()