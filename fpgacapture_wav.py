import socket
import numpy as np
import wave

ETH_P_ALL = 3
INTERFACE = "enp0s8"

FPGA_SRC_DEST = b"\x08\x00\x27\xfb\xdd\x66\xe8\x6a\x64\xe7\xe8\x30"

PACKET_SIZE = 2048
WORDS_PER_PACKET = 128          # adjust if different
NUM_PACKETS = 10000
SAMPLE_BYTES = 4
SAMPLE_RATE = 2.4e6 // 64
DTYPE = ">i4"                   # FPGA big-endian 32-bit

# ----------------------------
# Setup raw socket
# ----------------------------
s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ALL))
s.bind((INTERFACE, 0))

# Preallocate receive buffer (zero-copy target)
rx_buffer = bytearray(PACKET_SIZE)
rx_view = memoryview(rx_buffer)

# Preallocate full capture buffer
total_words = NUM_PACKETS * WORDS_PER_PACKET
capture_buffer = np.empty(total_words, dtype=DTYPE)

write_index = 0
packet_count = 0

print("Capturing packets...")

while packet_count < NUM_PACKETS:
    nbytes = s.recv_into(rx_buffer)

    # Fast header check (no slice copy)
    if rx_view[0:12] != FPGA_SRC_DEST:
        continue

    payload = rx_view[14:nbytes]

    # Zero-copy NumPy view of packet payload
    words = np.frombuffer(payload, dtype=DTYPE, count=WORDS_PER_PACKET)

    end_index = write_index + WORDS_PER_PACKET
    capture_buffer[write_index:end_index] = words

    write_index = end_index
    packet_count += 1

s.close()
print("Capture complete.")

# ----------------------------
# Signal Processing
# ----------------------------

# Convert to float (FIXED: must assign result)
a = capture_buffer.astype(np.float32)

# Remove DC offset
a -= np.mean(a)

# Normalize
max_val = np.max(np.abs(a))
if max_val > 0:
    a /= max_val

# Scale to 32-bit signed range
a *= (2**31 - 1)

# Convert to little-endian int32 for WAV
a_int = a.astype('<i4')

print("Writing WAV file...")

with wave.open("output.wav", "w") as fa:
    fa.setnchannels(1)
    fa.setsampwidth(SAMPLE_BYTES)   # 4 bytes (32-bit PCM)
    fa.setframerate(int(SAMPLE_RATE))
    fa.writeframes(a_int.tobytes())

print("Done.")
