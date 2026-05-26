import sys
import queue
import subprocess
import numpy as np
import sounddevice as sd
import whisper
from dotenv import load_dotenv
load_dotenv()
import database
from receptionist import Receptionist

SAMPLE_RATE = 16000
CHANNELS = 1
SILENCE_THRESHOLD = 0.01
SILENCE_DURATION = 1.5
MAX_RECORD_SECONDS = 15


def speak(text: str):
    print(f"\nAssistant: {text}\n")
    subprocess.run(["say", "-v", "Samantha", "-r", "175", text])


def listen(whisper_model) -> str | None:
    print("Listening...")
    audio_queue = queue.Queue()
    frames = []

    def callback(indata, frame_count, time_info, status):
        audio_queue.put(indata.copy())

    frames_per_chunk = int(SAMPLE_RATE * 0.1)
    required_silent = int(SILENCE_DURATION / 0.1)
    max_chunks = int(MAX_RECORD_SECONDS / 0.1)
    silent_count = 0
    has_speech = False

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS,
                        dtype="float32", blocksize=frames_per_chunk,
                        callback=callback):
        while len(frames) < max_chunks:
            try:
                chunk = audio_queue.get(timeout=1.0)
                frames.append(chunk)
                rms = np.sqrt(np.mean(chunk ** 2))
                if rms > SILENCE_THRESHOLD:
                    has_speech = True
                    silent_count = 0
                elif has_speech:
                    silent_count += 1
                    if silent_count >= required_silent:
                        break
            except queue.Empty:
                break

    if not has_speech or not frames:
        return None

    audio_data = np.concatenate(frames, axis=0).flatten()
    result = whisper_model.transcribe(audio_data, fp16=False, language="en")
    text = result["text"].strip()
    if text:
        print(f"You: {text}")
    return text if text else None


def select_business():
    businesses = database.get_all_businesses()
    if not businesses:
        print("\nNo businesses found. Run setup_business.py first.\n")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("  Select Business")
    print("=" * 50)
    for i, b in enumerate(businesses, 1):
        print(f"  {i}. {b['name']}  ({b['type']})")
    print("=" * 50)

    while True:
        try:
            choice = int(input("Enter number: "))
            if 1 <= choice <= len(businesses):
                return businesses[choice - 1]["id"]
        except ValueError:
            pass
        print("Invalid choice. Try again.")


def main():
    database.create_tables()

    print("Loading Whisper model...")
    whisper_model = whisper.load_model("base")
    print("Whisper ready.\n")

    business_id = select_business()

    try:
        receptionist = Receptionist(business_id)
    except ValueError as e:
        print(e)
        sys.exit(1)

    print("\n" + "=" * 50)
    print(f"  AI Receptionist — {receptionist.business['name']}")
    print("  Say 'exit' or 'bye' to end the call.")
    print("=" * 50 + "\n")

    # Opening greeting
    greeting = receptionist.greeting()
    speak(greeting)

    while not receptionist.is_done:
        user_input = listen(whisper_model)

        if not user_input:
            continue

        if any(w in user_input.lower() for w in ["exit", "quit", "bye", "goodbye", "stop"]):
            speak("Thank you for calling. Have a great day!")
            break

        try:
            response = receptionist.process(user_input)
            speak(response)
        except Exception as e:
            print(f"Error: {e}")
            speak("I'm sorry, something went wrong. Let me transfer you to our team.")
            break

    print("\nCall ended.")


if __name__ == "__main__":
    main()
