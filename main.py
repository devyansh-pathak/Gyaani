import threading
import keyboard
import time

from audio_module import audio_queue, start_recording, stop_recording
from hotkey_module import setup_hotkey
from paste_module import paste_text

def dummy_stt():
    count = 0
    while True:
        chunk = audio_queue.get()
        if chunk is None:
            break
        count +=1
    return(f"Recorded {count} chunks ({count * 1024} bytes)")

def worker():
    text = dummy_stt()
    time.sleep(5)
    print("Pasting:", text)
    paste_text(text)

def on_start():
    print("started")
    start_recording()
    threading.Thread(target = worker, daemon = True).start()

def on_stop():
    print("stopped")
    stop_recording()

if __name__ == "__main__":
    setup_hotkey(on_start, on_stop)
    print("Ready. Press Ctrl+Alt+R to start?stop recording. Press Ctrl+Alt+Q to quit.")
    keyboard.wait("ctrl+alt+q")