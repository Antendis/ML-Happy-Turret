from pymem import Pymem, process
import time

def main():
    # attach to GGST
    pm = Pymem("GGST-Win64-Shipping.exe")
    
    # get base address of the module
    module = process.module_from_name(pm.process_handle, "GGST-Win64-Shipping.exe").lpBaseOfDll
    
    # bullets offset you found in Cheat Engine
    bullets_offset = 0x4A5EB04
    
    # calculate final address
    bullets_addr = module + bullets_offset
    
    print("Monitoring GGST bullets... (Ctrl+C to stop)")
    
    try:
        while True:
            # read value (assuming it's an integer, but use read_float if CE showed it as a float)
            bullets = pm.read_int(bullets_addr)
            print("Bullets:", bullets)
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("Stopped.")

if __name__ == "__main__":
    main()
