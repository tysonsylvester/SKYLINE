import time, re, os, cv2, ctypes, winsound, subprocess, sys, traceback
import numpy as np
import pyautogui, keyboard, pyperclip
from pywinauto import Desktop
from PIL import ImageGrab

# ==============================
# 1. GLOBAL SETTINGS & SAFETY
# ==============================
pyautogui.FAILSAFE = False      
pyautogui.PAUSE = 0.2           # Increased global pause for OS stability
DPI_AWARENESS = True            

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

try:
    if DPI_AWARENESS:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# ==============================
# 2. SKYLINE BRIDGE
# ==============================
class SkylineBridge:
    def __init__(self):
        try: self.client = ctypes.windll.nvdaControllerClient
        except: self.client = None

    def say(self, text, cue_type=None):
        print(f"[Skyline] {text}")
        if cue_type == "ok": winsound.Beep(880, 100)
        if cue_type == "error": winsound.Beep(440, 250)
        if cue_type == "trap":
            for _ in range(3): winsound.Beep(1200, 50)

# ==============================
# 3. SKYLINE EXECUTOR
# ==============================
class SkylineExecutor:
    def __init__(self, bridge):
        self.bridge = bridge
        self.assets_path = get_resource_path("assets")

    def execute_step(self, step):
        step = step.strip()
        if not step: return

        # 7-SECOND RELIABLE LAUNCH
        if step.startswith("launch"):
            m = re.search(r'launch "(.+)"', step)
            if m:
                subprocess.Popen(m.group(1), shell=True)
                self.bridge.say("Launching... 7s buffer initiated.")
                time.sleep(7.0) 
                pyautogui.press('alt') # "Wake up" focus engine
                self.bridge.say("App should be ready.", cue_type="ok")

        elif step.startswith("wait"):
            m = re.search(r'wait "(\d+)"', step)
            if m: time.sleep(int(m.group(1)))

        elif step.startswith("type"):
            m = re.search(r'type "(.+)"', step)
            if m:
                # Force a click into the current window to lock focus
                pyautogui.click() 
                time.sleep(0.5)
                # Slow, steady typing to prevent character duplication
                pyautogui.write(m.group(1), interval=0.1)
                pyautogui.press('enter')

        elif step == "home":
            pyautogui.moveTo(20, 20)

# ==============================
# 4. MAIN INTERFACE
# ==============================
def main():
    bridge = SkylineBridge()
    exec_engine = SkylineExecutor(bridge)
    bridge.say("Skyline Ready.", cue_type="ok")

    def trigger():
        try:
            raw = pyperclip.paste()
            if not raw: return
            cmd = raw.encode('ascii', 'ignore').decode().strip()
            for step in cmd.split("->"):
                exec_engine.execute_step(step)
                time.sleep(1.0) # 1-second delay between every single command
            bridge.say("Sequence Finished.", cue_type="ok")
        except Exception:
            bridge.say("Error.", cue_type="error")

    keyboard.add_hotkey("ctrl+shift+d", trigger)
    keyboard.wait()

if __name__ == "__main__":
    main()