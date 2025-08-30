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

    # Addresses
    p1_bullets = module + 0x4A5EB04
    p2_bullets = module + 0x4A5ED5C
    p1_x = module + 0x4A5EEF4
    p2_x = module + 0x4A5EC9C
    p1_conc = module + 0x4A5EAFC
    p2_conc = module + 0x4A5ED54
    p1_health = module + 0x4A5EA60
    p2_health = module + 0x4A5ECB8

    max_health = 420  # In-game max health
    max_conc = 1.0    # Concentration normalized to 1.0

    print("Detecting which player is you (fire one bullet at start)...")
    your_player = None
    opponent = None

    # Initial bullets
    p1_bullets_val = pm.read_int(p1_bullets)
    p2_bullets_val = pm.read_int(p2_bullets)

    while your_player is None:
        new_p1_bullets = pm.read_int(p1_bullets)
        new_p2_bullets = pm.read_int(p2_bullets)
        if new_p1_bullets < p1_bullets_val:
            your_player = "P1"
            opponent = "P2"
        elif new_p2_bullets < p2_bullets_val:
            your_player = "P2"
            opponent = "P1"
        time.sleep(0.05)

    print(f"Your player: {your_player} | Opponent: {opponent}")
    print("Monitoring GGST HUD... (Ctrl+C to stop)")

    try:
        while True:
            # Read bullets
            p1_bullets_val = pm.read_int(p1_bullets)
            p2_bullets_val = pm.read_int(p2_bullets)

            # Read positions
            p1_x_val = read_float(pm, p1_x)
            p2_x_val = read_float(pm, p2_x)

            # Read health
            p1_health_val = read_float(pm, p1_health) * max_health
            p2_health_val = read_float(pm, p2_health) * max_health

            # Read concentration
            p1_conc_val = read_float(pm, p1_conc) * 100  # scale to 0–100%
            p2_conc_val = read_float(pm, p2_conc) * 100  # scale to 0–100%

            # Map dynamically based on which player is you
            if your_player == "P1":
                your_bullets_val = p1_bullets_val
                your_x_val = p1_x_val
                your_conc_val = p1_conc_val
                your_health_val = p1_health_val
                opp_x_val = p2_x_val
                opp_health_val = p2_health_val
            else:
                your_bullets_val = p2_bullets_val
                your_x_val = p2_x_val
                your_conc_val = p2_conc_val
                your_health_val = p2_health_val
                opp_x_val = p1_x_val
                opp_health_val = p1_health_val

            # Determine left/right sides
            if your_x_val > opp_x_val:
                your_side = "Right"
                opp_side = "Left"
            else:
                your_side = "Left"
                opp_side = "Right"

            # Print HUD in requested order
            print(f"Bullets: {your_bullets_val} | Conc: {your_conc_val:.1f}% | HP: {your_health_val:.1f} | Pos: {your_x_val:.2f} | "
                  f"Opponent HP: {opp_health_val:.1f} | Opponent Pos: {opp_x_val:.2f}")

            time.sleep(0.15)

    except KeyboardInterrupt:
        print("Stopped.")

if __name__ == "__main__":
    main()
