import time

import pyautogui
import pyperclip 

def paste_text(text):
    try:
        old_clipboard = pyperclip.paste()
    except Exception:
        old_clipboard = ""

    pyperclip.copy(text)
    time.sleep(0.15)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.25)
    pyperclip.copy(old_clipboard)

# TEST 
if __name__ == "__main__":
    print("Open Notepad and click inside it. Pasting in 5 seconds...")
    time.sleep(5)
    paste_text("kal meeting reschedule kar dena")
    paste_text(" कल मीटिंग रीशेड्यूल कर देना")
    print("Done.")



