import asyncio
import time
from dotenv import load_dotenv
from paste_module import paste_text
from hotkey_module import setup_hotkeys
from mic_stt import start_stt_stream
from ui_overlay import launch_overlay
from model import (
    handle_f8_trigger,
    on_transcript_received as model_on_transcript,
    get_latest_output,
)

load_dotenv()

# Track whether Ctrl+R dictation mode is active
dictation_active = False
overlay = None


def on_dictation_start():
    global dictation_active
    dictation_active = True
    print("\n" + "=" * 60)
    print("🟢 [Ctrl+R] VOICE DICTATION MODE ON")
    print("👉 Speak into the mic — words will be pasted directly into active app.")
    print("👉 Press [Ctrl+R] again to STOP dictation.")
    print("=" * 60)

    if overlay:
        overlay.set_mode("DICTATION", "Dictating")
        overlay.update_current("Listening to voice... (Ctrl+R to stop)")


def on_dictation_stop():
    global dictation_active
    dictation_active = False
    print("\n" + "=" * 60)
    print("🔴 [Ctrl+R] VOICE DICTATION MODE OFF")
    print("=" * 60)

    if overlay:
        overlay.set_mode("IDLE", "Ready")
        overlay.update_current("Dictation stopped. Press [Ctrl+R] or [F8]")


async def on_stt_transcript(text: str):
    """
    Called whenever a transcript arrives from Gnani STT WebSocket.
    """
    global dictation_active

    # Always feed transcript to model so it has latest command
    model_on_transcript(text)

    # When Ctrl+R dictation is active: ONLY listen and paste directly!
    if dictation_active:
        print(f"✍️  [Dictating]: {text}")
        paste_text(text + " ")
        if overlay:
            overlay.push_lyric(text)
    else:
        # Show incoming speech dynamically in the lyric overlay
        if overlay and overlay.mode == "IDLE":
            overlay.update_current(text)


def trigger_llm(loop):
    """Called when F8 is pressed."""
    print("\n" + "=" * 60)
    print("⚡ [F8 Pressed] Starting LLM Transform Function...")
    print("=" * 60)
    if overlay:
        overlay.set_mode("AI_LISTENING", "Reading Text")
    asyncio.run_coroutine_threadsafe(handle_f8_trigger(), loop)


async def main():
    global overlay
    loop = asyncio.get_running_loop()

    # Launch the sleek bottom-anchored floating lyric overlay
    print("🎨 Launching Voice Lyrics UI Overlay...")
    overlay = launch_overlay()

    # Setup hotkeys: Ctrl+R for dictation, F8 for LLM
    setup_hotkeys(
        on_dictation_start=on_dictation_start,
        on_dictation_stop=on_dictation_stop,
        on_f8=lambda: trigger_llm(loop),
    )

    print("=" * 65)
    print("🚀 GYAANI AI DUAL-MODE SYSTEM READY")
    print("=" * 65)
    print("📌 MODE 1 [Ctrl+R]: Live Voice Dictation & Direct Paste")
    print("   Press Ctrl+R -> Speak -> Words paste directly into active app.")
    print("   Press Ctrl+R again to stop.")
    print("")
    print("📌 MODE 2 [F8]: AI Text Transformation (LLM)")
    print("   Highlight text in any app -> Press F8 -> Speak instruction ->")
    print("   LLM transforms text and replaces it in place.")
    print("=" * 65)
    print("Press Ctrl+C to exit.\n")

    # Start continuous microphone STT stream
    await start_stt_stream(on_transcript=on_stt_transcript)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
        if overlay:
            overlay.close()

        if overlay:
            overlay.close()