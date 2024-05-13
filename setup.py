import os
import time

LIBRARIES = {
    "logging": "logging",
    "py-cord": "discord",
    "asyncio": "asyncio",
    "datetime": "datetime",
    "pyautogui": "pyautogui",
}

def installdeps():
    
    global LIBRARIES
    
    try:
        for lib in LIBRARIES:
            try:
                __import__(LIBRARIES[lib])
                print(f"[{time.strftime('%H:%M:%S')}] Already installed {lib}!")
            except:	
                print(f"[{time.strftime('%H:%M:%S')}] Installing {lib}... \r")
                os.system(f"pip -q install {lib}")
                try:
                    __import__(LIBRARIES[lib])
                    print(f"[{time.strftime('%H:%M:%S')}] Succesfully installed {lib}!")
                except:	
                    print(f"[{time.strftime('%H:%M:%S')}] Failed to install {lib}!")
                    print(f"[{time.strftime('%H:%M:%S')}] Please install {lib} manually!")
        return True             
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Failed to install libraries! {e}")
        return False
                    
                    
if __name__ == "__main__":
    check = installdeps()
    if check:
        print(f"[{time.strftime('%H:%M:%S')}] Installed all libraries!")