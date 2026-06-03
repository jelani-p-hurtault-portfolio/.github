import random
import argparse
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wavfile

SONG_STRUCTURES = ["AABB/CC", "ABAB/CD", "AB/CDDD"]

CHORD_LOOPS = [
    ["I", "IV", "ii", "V"],
    ["I", "vi", "ii", "V"],
    ["I", "iii", "IV", "iv"],
    ["I", "V", "ii", "V"],
    ["I", "vi", "IV", "V"],
    ["IV", "I", "vi", "IV"],
    ["I", "V", "vi", "I"],
    ["I", "IV", "iv", "I"],
    ["IV", "V", "I", "I"],
    ["vi", "IV", "I", "V"],
]

NOTES = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
MAJOR_SCALE_STEPS = [0, 2, 4, 5, 7, 9, 11]
ROMAN_TO_SCALE = {
    "I": 0, "ii": 1, "iii": 2, "IV": 3,
    "V": 4, "vi": 5, "vii": 6
}
CHORD_INTERVALS = {
    "I":   [0, 4, 7],
    "ii":  [0, 3, 7],
    "iii": [0, 3, 7],
    "IV":  [0, 4, 7],
    "V":   [0, 4, 7],
    "vi":  [0, 3, 7],
    "iv":  [0, 3, 7],
    "vii": [0, 3, 6],
}

SAMPLE_RATE = 48000

def pick_key():
    return random.randint(57, 69)

def pick_tempo():
    return random.randint(80, 160)

def pick_structure():
    return random.choice(SONG_STRUCTURES)

def get_labels(structure):
    letters = []
    for ch in structure:
        if ch.isalpha() and ch not in letters:
            letters.append(ch)
    return letters

def assign_loops(labels):
    pool = random.sample(CHORD_LOOPS, len(labels))
    return {label: pool[i] for i, label in enumerate(labels)}

def build_song(structure, loop_map):
    clean = structure.replace("/", "")
    return [loop_map[ch] for ch in clean]

def midi_to_name(midi):
    return NOTES[midi % 12] + str(midi // 12 - 1)

def midi_to_freq(midi):
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))

def get_scale_notes(root_midi):
    return [root_midi + step for step in MAJOR_SCALE_STEPS]

def get_chord_notes(root_midi, roman):
    scale = get_scale_notes(root_midi)
    degree = ROMAN_TO_SCALE[roman]
    chord_root = scale[degree]
    return [chord_root + i for i in CHORD_INTERVALS[roman]]

def get_chord_root(root_midi, roman):
    scale = get_scale_notes(root_midi)
    return scale[ROMAN_TO_SCALE[roman]]

def pick_melody_note(chord_notes, scale_notes):
    if random.random() < 0.8:
        return random.choice(chord_notes)
    return random.choice(scale_notes)

def generate_melody(song, key):
    scale = get_scale_notes(key)
    all_notes = []
    for measure_chords in song:
        for roman in measure_chords:
            chord_notes = get_chord_notes(key, roman)
            measure_melody = [pick_melody_note(chord_notes, scale) for _ in range(8)]
            all_notes.append(measure_melody)
    return all_notes

def generate_bass_notes(song, key):
    bass_notes = []
    for measure_chords in song:
        for roman in measure_chords:
            chord_root = get_chord_root(key, roman)
            bass_notes.append(chord_root - 24)
    return bass_notes

def sawtooth_wave(freq, duration, amplitude=0.3):
    num_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    wave = 2.0 * (t * freq - np.floor(t * freq + 0.5))
    return (wave * amplitude).astype(np.float32)

def render_melody(melody, tempo):
    beat_duration = 60.0 / tempo
    eighth_duration = beat_duration / 2.0
    chunks = []
    for measure in melody:
        for midi_note in measure:
            freq = midi_to_freq(midi_note)
            chunks.append(sawtooth_wave(freq, eighth_duration))
    return np.concatenate(chunks)

def render_bass(bass_notes, tempo):
    beat_duration = 60.0 / tempo
    measure_duration = beat_duration * 4.0
    chunks = []
    for midi_note in bass_notes:
        freq = midi_to_freq(midi_note)
        chunks.append(sawtooth_wave(freq, measure_duration, amplitude=0.2))
    return np.concatenate(chunks)

def save_wav(filename, audio):
    data = (audio * 32767).astype(np.int16)
    wavfile.write(filename, SAMPLE_RATE, data)

parser = argparse.ArgumentParser()
parser.add_argument("--output", type=str, default=None)
parser.add_argument("--bass", action="store_true")
args = parser.parse_args()

key = pick_key()
tempo = pick_tempo()
structure = pick_structure()
labels = get_labels(structure)
loop_map = assign_loops(labels)
song = build_song(structure, loop_map)
melody = generate_melody(song, key)

print("Key:", midi_to_name(key))
print("Tempo:", tempo, "BPM")
print("Structure:", structure)

melody_audio = render_melody(melody, tempo)

if args.bass:
    bass_notes = generate_bass_notes(song, key)
    bass_audio = render_bass(bass_notes, tempo)
    min_len = min(len(melody_audio), len(bass_audio))
    audio = melody_audio[:min_len] + bass_audio[:min_len]
else:
    audio = melody_audio

audio = np.clip(audio, -1.0, 1.0)

if args.output:
    save_wav(args.output, audio)
    print("Saved to", args.output)
else:
    sd.play(audio, SAMPLE_RATE)
    sd.wait()