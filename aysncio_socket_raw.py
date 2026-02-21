import asyncio
import socket
import struct
from socket import AF_PACKET, SOCK_RAW, htons

# Define constant for all ethernet protocols (Linux specific)
ETH_P_ALL = 0x0003

async def raw_socket_receiver(sock):
    """Asynchronously receives data from a raw socket."""
    loop = asyncio.get_running_loop()
    print("Waiting for packets...")
    while True:
        # sock_recv returns the data
        try:
            data = await loop.sock_recv(sock, 65535) # Max IP packet size
            if not data:
                break
            print(f"Received packet of length: {len(data)} bytes")
            # Further packet parsing can happen here
        except BlockingIOError:
            # Should not happen with sock_recv but good practice
            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Error receiving data: {e}")
            break

def create_raw_socket():
    """Creates and configures a non-blocking raw socket."""
    # AF_PACKET is specific to Linux for link layer access
    # SOCK_RAW for raw packets
    # htons(ETH_P_ALL) specifies all protocols in network byte order
    s = socket.socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL))
    s.setblocking(False) # Must be non-blocking for asyncio
    return s

async def main():
    raw_sock = create_raw_socket()
    # You might want to bind to a specific interface using SO_BINDTODEVICE

    # Create and run the receiver task
    await raw_socket_receiver(raw_sock)
    
    raw_sock.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Receiver stopped by user")

