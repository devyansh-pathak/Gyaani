import time
import pyautogui
import pyperclip 

pyautogui.PAUSE = 0.05


def paste_text(text: str):
    """
    Pastes given text into the active window at the cursor or replaces selected text.
    Restores the user's previous clipboard content afterwards.
    """
    if not text or not str(text).strip():
        return

    try:
        old_clipboard = pyperclip.paste()
    except Exception:
        old_clipboard = ""

    pyperclip.copy(text)
    time.sleep(0.05)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.15)

    try:
        pyperclip.copy(old_clipboard)
    except Exception:
        pass
