import queue

import sounddevice as sd

SAMPLE_RATE = 16000
CHANNELS = 1
BLOCKSIZE = 512

audio_queue = queue.Queue()
_stream = None

def _callback(indata, frames, time_info, status):
    """called by sounddevice for every chunk. It just copy bytes to the queue."""
    audio_queue.put(bytes(indata))

def start_recording():
    global _stream
    if _stream is not None:
        return
    _stream = sd.RawInputStream(
        samplerate = SAMPLE_RATE,
        channels = CHANNELS,
        dtype = "int16",
        blocksize = BLOCKSIZE,
        callback = _callback
    )
    _stream.start()

def stop_recording():
    global _stream 
    if _stream is None:
        return
    _stream.stop()
    _stream.close()
    _stream = None
    audio_queue.put(None)

# TEST
if __name__  == "__main__":
    import time
    import wave
    import winsound

    print("recording for 4 seconds... Speak now!")
    start_recording()
    time.sleep(4)
    stop_recording()

    chunks = []
    while True:
        chunk = audio_queue.get()
        if chunk is None:
            break
        chunks.append(chunk)

    print(f"Got {len(chunks)} chunks, each{len(chunks[0]) if chunks else 0}bytes")

    with wave.open("test.wav", "wb")as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        f.writeframes(b"".join(chunks))

    print("Saved test.wav . Playing it back...")
    winsound.PlaySound("test.wav", winsound.SND_FILENAME)
    print("Done.")

