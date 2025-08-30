from pymem import Pymem, process
import struct
import time

def read_float(pm, address):
    """Reads a 32-bit float from memory"""
    data = pm.read_bytes(address, 4)
    return struct.unpack('f', data)[0]

def main():
    pm = Pymem("GGST-Win64-Shipping.exe")
    module = process.module_from_name(pm.process_handle, "GGST-Win64-Shipping.exe").lpBaseOfDll

    # Your bullets (green static address)
    bullets_offset = 0x4A5EB04
    bullets_addr = module + bullets_offset

    # Player X positions (green static addresses)
    p1_x_offset = 0x4A5EEF4
    p2_x_offset = 0x4A5EC9C
    p1_addr = module + p1_x_offset
    p2_addr = module + p2_x_offset

    print("Monitoring GGST bullets and player positions... (Ctrl+C to stop)")
    
    try:
        while True:
            bullets = pm.read_int(bullets_addr)  # or read_float if bullets are float
            p1_x = read_float(pm, p1_addr)
            p2_x = read_float(pm, p2_addr)

            # Determine left/right
            if p1_x > p2_x:
                p1_side = "Right"
                p2_side = "Left"
            else:
                p1_side = "Left"
                p2_side = "Right"

            # Print in compact single-line format
            print(f"Bullets: {bullets} | P1: {p1_side} ({p1_x:.2f}) | P2: {p2_side} ({p2_x:.2f})")
            time.sleep(0.15)
    except KeyboardInterrupt:
        print("Stopped.")

if __name__ == "__main__":
    main()
