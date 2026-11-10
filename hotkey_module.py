import keyboard

HOTKEY = "ctrl+alt+r"

_recording = False
_on_start = None
_on_stop = None

def _toggle():
    """ Runs everytime the Hotkey is pressed."""
    global _recording
    if not _recording:
        _recording = True
        _on_start()
    else:
        _recording = False
        _on_stop()

def setup_hotkey(on_start, on_stop):
    """Tell the module which fxns to call on start and stop."""
    global _on_start, _on_stop
    _on_start = on_start
    _on_stop = on_stop
    keyboard.add_hotkey(HOTKEY, _toggle)

# TEST
if __name__ == "__main__":
    setup_hotkey(lambda: print("started"), lambda: print("stopped"))
    print(f"Press {HOTKEY.upper()} to start/stop. Press Esc to quit.")
    keyboard.wait("esc")
