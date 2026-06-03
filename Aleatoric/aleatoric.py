import random

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

def get_scale_notes(root_midi):
    return [root_midi + step for step in MAJOR_SCALE_STEPS]

def get_chord_notes(root_midi, roman):
    scale = get_scale_notes(root_midi)
    degree = ROMAN_TO_SCALE[roman]
    chord_root = scale[degree]
    intervals = CHORD_INTERVALS[roman]
    return [chord_root + i for i in intervals]

def pick_melody_note(chord_notes, scale_notes):
    if random.random() < 0.8:
        return random.choice(chord_notes)
    else:
        return random.choice(scale_notes)

def generate_melody(song, key):
    scale = get_scale_notes(key)
    all_notes = []
    for measure_chords in song:
        for roman in measure_chords:
            chord_notes = get_chord_notes(key, roman)
            measure_melody = []
            for _ in range(8):
                note = pick_melody_note(chord_notes, scale)
                measure_melody.append(note)
            all_notes.append(measure_melody)
    return all_notes

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
print()
for i, measure in enumerate(melody):
    names = [midi_to_name(n) for n in measure]
    print(f"Measure {i+1}: {names}")