import socket
import asyncio

def create_raw_socket(interface):
    # AF_PACKET allows capturing raw ethernet frames
    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
    sock.bind((interface, 0))
    sock.setblocking(False)  # Essential for asyncio
    return sock
async def listen_interface(sock, name):
    loop = asyncio.get_running_loop()
    while True:
        # Wait for data without blocking other tasks
        data = await loop.sock_recv(sock, 4096)
        print(f"[{name}] Received: {len(data)} bytes")
        # Process RFoF frame here

async def main():
    sock1 = create_raw_socket("eth0")
    sock2 = create_raw_socket("eth1")

    # Run both listeners concurrently using gather
    await asyncio.gather(
        listen_interface(sock1, "IFACE_1"),
        listen_interface(sock2, "IFACE_2")
    )

if __name__ == "__main__":
    asyncio.run(main())
