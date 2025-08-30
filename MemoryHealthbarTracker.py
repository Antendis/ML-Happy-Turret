import pymem
import time

# Attach to Guilty Gear Strive process
PROCESS_NAME = "GGST-Win64-Shipping.exe"
HEALTH_ADDR = 0x23F246B597C  # Replace this each session with Cheat Engine's found address

pm = pymem.Pymem(PROCESS_NAME)

print(f"[+] Attached to {PROCESS_NAME} (pid {pm.process_id})")
print(f"[+] Monitoring HP at address: {hex(HEALTH_ADDR)}\n")

try:
    while True:
        try:
            hp = pm.read_int(HEALTH_ADDR)
            print(f"Current HP: {hp}")
        except pymem.exception.MemoryReadError:
            print("[!] Failed to read HP (invalid address or process not accessible).")
            break

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n[+] Exiting...")
