import asyncio
import json
import os
import numpy as np
import websockets
import sounddevice as sd
from dotenv import load_dotenv

try:
    from ui_overlay import get_overlay
except ImportError:
    get_overlay = lambda: None

load_dotenv()
API_KEY = os.getenv("API_KEY")
HEADERS = {
    "x-api-key-id": API_KEY,
    "language_code": "indic-auto",
    "x-sample-rate": "16000",
    "format": "transliterate",
}


async def start_stt_stream(on_transcript=None):
    """
    Continuously streams mic audio to Gnani STT WebSocket.
    Calls `on_transcript(text)` whenever a new transcript arrives.
    Also feeds dynamic real-time voice volume levels to the mini pill overlay.
    """
    loop = asyncio.get_running_loop()
    q = asyncio.Queue()
    overlay = get_overlay()

    def cb(indata, frames, t, status):
        # 1. Put raw audio bytes into STT queue
        loop.call_soon_threadsafe(q.put_nowait, bytes(indata))

        # 2. Feed dynamic voice volume to mini pill visualizer
        try:
            if overlay and overlay.is_running:
                audio_arr = np.frombuffer(indata, dtype=np.int16)
                peak = float(np.max(np.abs(audio_arr))) / 32768.0
                overlay.feed_volume(peak)
        except Exception:
            pass

    uri = "wss://api.vachana.ai/stt/v3/stream"
    async with websockets.connect(uri, additional_headers=HEADERS) as ws:
        async def send():
            with sd.RawInputStream(samplerate=16000, channels=1, dtype="int16", blocksize=512, callback=cb):
                while True:
                    await ws.send(await q.get())

        async def recv():
            async for raw in ws:
                m = json.loads(raw)
                if m.get("type") == "transcript":
                    text = m.get("text", "").strip()
                    if text:
                        print(f">> [STT]: {text}")
                        if on_transcript:
                            if asyncio.iscoroutinefunction(on_transcript):
                                await on_transcript(text)
                            else:
                                on_transcript(text)
                elif m.get("type") == "error":
                    print("STT ERROR:", m.get("message"))

        print("🟢 Mic STT Listener activated!")
        await asyncio.gather(send(), recv())


# Alias for backward compatibility
listener = start_stt_stream

if __name__ == "__main__":
    try:
        asyncio.run(listener())
    except KeyboardInterrupt:
        print("\nclosed")
