import keyboard

HOTKEY_DICTATION = "ctrl+r"
HOTKEY_LLM = "f8"

_recording = False
_on_dictation_start = None
_on_dictation_stop = None
_on_f8_trigger = None


def _toggle_dictation():
    """Toggles dictation listening on and off when Ctrl+R is pressed."""
    global _recording
    if not _recording:
        _recording = True
        if _on_dictation_start:
            _on_dictation_start()
    else:
        _recording = False
        if _on_dictation_stop:
            _on_dictation_stop()


def setup_hotkeys(on_dictation_start, on_dictation_stop, on_f8):
    """
    Sets up global hotkeys:
    - Ctrl+R: Start / Stop microphone listening and direct text pasting
    - F8: Start LLM transformation on selected text
    """
    global _on_dictation_start, _on_dictation_stop, _on_f8_trigger
    _on_dictation_start = on_dictation_start
    _on_dictation_stop = on_dictation_stop
    _on_f8_trigger = on_f8

    keyboard.add_hotkey(HOTKEY_DICTATION, _toggle_dictation)
    keyboard.add_hotkey(HOTKEY_LLM, lambda: _on_f8_trigger() if _on_f8_trigger else None)


# Backward-compatibility alias
def setup_hotkey(on_start, on_stop):
    global _on_dictation_start, _on_dictation_stop
    _on_dictation_start = on_start
    _on_dictation_stop = on_stop
    keyboard.add_hotkey(HOTKEY_DICTATION, _toggle_dictation)


if __name__ == "__main__":
    setup_hotkeys(
        on_dictation_start=lambda: print("Dictation started"),
        on_dictation_stop=lambda: print("Dictation stopped"),
        on_f8=lambda: print("F8 LLM triggered"),
    )
    print(f"Press {HOTKEY_DICTATION.upper()} to start/stop dictation.")
    print(f"Press {HOTKEY_LLM.upper()} for LLM function.")
    print("Press Esc to quit.")
    keyboard.wait("esc")
