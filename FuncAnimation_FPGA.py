import socket
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

ETH_P_ALL = 3
INTERFACE = "eth0"

FPGA_SRC_DEST = b"\x08\x00\x27\xfb\xdd\x65\xe8\x6a\x64\xe7\xe8\x30"

PACKET_SIZE = 2048
WORDS_PER_PACKET = 256
DTYPE = ">i4"

# ---------------------------
# Setup raw socket
# ---------------------------
s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ALL))
s.bind((INTERFACE, 0))
s.setblocking(False)

# Preallocate receive buffer (zero-copy target)
rx_buffer = bytearray(PACKET_SIZE)
rx_view = memoryview(rx_buffer)

# Preallocate numpy sample buffer
sample_buffer = np.zeros(WORDS_PER_PACKET, dtype=DTYPE)

# Preallocate FFT buffer
fft_buffer = np.zeros(WORDS_PER_PACKET)


# ---------------------------
# Fast packet poller
# ---------------------------
def poll_socket():
    try:
        nbytes = s.recv_into(rx_buffer)
    except BlockingIOError:
        return

    # Fast header check (no copy)
    if rx_view[0:12] != FPGA_SRC_DEST:
        return

    payload = rx_view[14:nbytes]

    # Zero-copy numpy view
    samples = np.frombuffer(payload, dtype=DTYPE, count=WORDS_PER_PACKET)

    # Copy once into stable buffer
    sample_buffer[:] = samples


# ---------------------------
# Matplotlib Setup
# ---------------------------
fig, ax = plt.subplots()
ax.set_xlim(0, WORDS_PER_PACKET)
ax.set_ylim(0, 25)  # adjust as needed
line, = ax.plot([], [], lw=1)

x_axis = np.arange(WORDS_PER_PACKET)


def init():
    line.set_data([], [])
    return line,


def animate(_):
    # Poll socket as fast as possible
    poll_socket()

    # FFT
    fft_vals = np.fft.fft(sample_buffer)
    fft_shifted = np.fft.fftshift(fft_vals)

    # Avoid log(0)
    magnitude = np.log(np.abs(fft_shifted) + 1)

    line.set_data(x_axis, magnitude)
    return line,


anim = FuncAnimation(
    fig,
    animate,
    init_func=init,
    interval=5,      # small interval for fast update
    blit=True
)

plt.show()
