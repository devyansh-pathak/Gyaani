import time
import ctypes
import ctypes.wintypes
import pyautogui
import pyperclip

# Reduce pyautogui pause for responsive clipboard capture
pyautogui.PAUSE = 0.05


def get_selected_text(timeout: float = 0.5, restore_clipboard: bool = True) -> str:
    """
    Grabs whatever text is currently selected in ANY application window.

    Steps:
    1. Saves existing clipboard content so it isn't lost.
    2. Clears clipboard to prevent reading stale text.
    3. Simulates 'Ctrl+C' in the active window.
    4. Polls until the newly selected text appears in the clipboard.
    5. Restores original clipboard content (if restore_clipboard is True).
    6. Returns the captured string.
    """
    try:
        old_clipboard = pyperclip.paste()
    except Exception:
        old_clipboard = ""

    # Clear clipboard
    pyperclip.copy("")

    # Simulate Ctrl+C in whichever window currently has focus
    pyautogui.hotkey("ctrl", "c")

    # Wait for text to arrive in clipboard
    selected_text = ""
    start_time = time.time()
    while time.time() - start_time < timeout:
        time.sleep(0.025)
        text = pyperclip.paste()
        if text:
            selected_text = text
            break

    # Restore previous clipboard content
    if restore_clipboard:
        try:
            pyperclip.copy(old_clipboard)
        except Exception:
            pass

    return selected_text


def run_hotkey_listener(vk_key: int = 0x77):  # Default: F8 key (VK_F8 = 0x77)
    """
    Listens for a global hotkey (F8) in the background.
    Whenever you press F8 in ANY app, it captures the selected text into `selected_text`.
    """
    user32 = ctypes.windll.user32
    HOTKEY_ID = 1
    MOD_NOREPEAT = 0x4000

    if not user32.RegisterHotKey(None, HOTKEY_ID, MOD_NOREPEAT, vk_key):
        print("❌ Failed to register F8 hotkey (might be used by another app).")
        return

    print("=" * 60)
    print("🟢 Global Hotkey Listener Active!")
    print("👉 Kisi bhi app mein text select karo aur [ F8 ] press karo.")
    print("👉 Selected text variable 'selected_text' mein store ho jayega.")
    print("Press Ctrl+C in this terminal to exit.")
    print("=" * 60)

    try:
        msg = ctypes.wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            if msg.message == 0x0312:  # WM_HOTKEY
                # Text gets captured and stored in variable
                selected_text = get_selected_text()

                if selected_text.strip():
                    print("\n[F8 Pressed] Captured text into variable 'selected_text':")
                    print("-" * 50)
                    print(selected_text)
                    print("-" * 50)
                    return selected_text 
                else:
                    print("\n[F8 Pressed] Koi text select nahi mila.")
                    return None

            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
    except KeyboardInterrupt:
        print("\nStopping hotkey listener...")
    finally:
        user32.UnregisterHotKey(None, HOTKEY_ID)


if __name__ == "__main__":
    run_hotkey_listener()
