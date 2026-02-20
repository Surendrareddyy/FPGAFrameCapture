import socket
import numpy as np

INTERFACE = "eth0"
HEADER_SIZE = 32   # total header including Ethernet

sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
sock.bind((INTERFACE, 0))

print("Listening...")

while True:
    packet, _ = sock.recvfrom(65535)

    if len(packet) <= HEADER_SIZE:
        continue

    payload = packet[HEADER_SIZE:]

    samples = np.frombuffer(payload, dtype=np.int16)

    print(samples[:10])
