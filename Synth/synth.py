import mido

ports = mido.get_input_names()

if not ports:
    print("No MIDI input ports found.")
    exit()

print("Available ports:")
for p in ports:
    print(" ", p)

port_name = ports[0]
print(f"\nListening on: {port_name}")

with mido.open_input(port_name) as port:
    for msg in port:
        print(msg)