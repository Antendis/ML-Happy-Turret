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

    # Bullets addresses
    p1_bullets_offset = 0x4A5EB04
    p2_bullets_offset = 0x4A5ED5C
    p1_bullets_addr = module + p1_bullets_offset
    p2_bullets_addr = module + p2_bullets_offset

    # Player X positions
    p1_x_offset = 0x4A5EEF4
    p2_x_offset = 0x4A5EC9C
    p1_x_addr = module + p1_x_offset
    p2_x_addr = module + p2_x_offset

    print("Detecting which player is you...")
    your_player = None
    opponent = None

    # Read initial bullets
    p1_bullets = pm.read_int(p1_bullets_addr)
    p2_bullets = pm.read_int(p2_bullets_addr)

    print("Start firing one bullet to detect your side...")

    while your_player is None:
        new_p1_bullets = pm.read_int(p1_bullets_addr)
        new_p2_bullets = pm.read_int(p2_bullets_addr)

        if new_p1_bullets < p1_bullets:
            your_player = "P1"
            opponent = "P2"
        elif new_p2_bullets < p2_bullets:
            your_player = "P2"
            opponent = "P1"

        time.sleep(0.05)

    print(f"Your player: {your_player} | Opponent: {opponent}")
    print("Monitoring bullets and positions... (Ctrl+C to stop)")

    try:
        while True:
            p1_bullets = pm.read_int(p1_bullets_addr)
            p2_bullets = pm.read_int(p2_bullets_addr)
            p1_x = read_float(pm, p1_x_addr)
            p2_x = read_float(pm, p2_x_addr)

            # Map dynamically
            if your_player == "P1":
                your_bullets = p1_bullets
                your_x = p1_x
                opp_bullets = p2_bullets
                opp_x = p2_x
            else:
                your_bullets = p2_bullets
                your_x = p2_x
                opp_bullets = p1_bullets
                opp_x = p1_x

            # Determine left/right
            if your_x > opp_x:
                your_side = "Right"
                opp_side = "Left"
            else:
                your_side = "Left"
                opp_side = "Right"

            print(f"Bullets: {your_bullets} | You: {your_side} ({your_x:.2f}) | Opponent: {opp_side} ({opp_x:.2f})")
            time.sleep(0.15)
    except KeyboardInterrupt:
        print("Stopped.")

if __name__ == "__main__":
    main()
