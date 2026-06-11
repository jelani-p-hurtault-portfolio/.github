import mido
import sounddevice as sd

print("MIDI input ports:")
for port in mido.get_input_names():
    print(" ", port)

print()
print("Audio output devices:")
for i, dev in enumerate(sd.query_devices()):
    if dev["max_output_channels"] > 0:
        print(f"  {i}: {dev['name']}")