import sys
import queue
import subprocess
import numpy as np
import sounddevice as sd
import whisper
import ollama

SAMPLE_RATE = 16000
CHANNELS = 1
SILENCE_THRESHOLD = 0.01
SILENCE_DURATION = 1.5  # seconds of silence to stop recording
MAX_RECORD_SECONDS = 15

SYSTEM_PROMPT = """You are a helpful AI voice assistant. Keep all responses short, clear, and conversational — under 3 sentences unless asked for more. Never use markdown, bullet points, or special symbols. Speak naturally like a human."""


class VoiceAssistant:
    def __init__(self):
        print("Loading Whisper speech model (first run may take a moment)...")
        self.whisper_model = whisper.load_model("base")
        print("Whisper ready.")

        self.conversation_history = []

    def speak(self, text: str):
        print(f"\nAssistant: {text}\n")
        subprocess.run(["say", "-v", "Samantha", "-r", "175", text])

    def listen(self) -> str | None:
        print("Listening... (speak now)")
        audio_queue = queue.Queue()
        frames = []

        def callback(indata, frame_count, time_info, status):
            audio_queue.put(indata.copy())

        silent_frames = 0
        frames_per_check = int(SAMPLE_RATE * 0.1)  # 100ms chunks
        required_silent_frames = int(SILENCE_DURATION / 0.1)
        max_frames = int(MAX_RECORD_SECONDS / 0.1)
        has_speech = False

        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS,
                            dtype="float32", blocksize=frames_per_check,
                            callback=callback):
            while len(frames) < max_frames:
                try:
                    chunk = audio_queue.get(timeout=1.0)
                    frames.append(chunk)
                    rms = np.sqrt(np.mean(chunk ** 2))
                    if rms > SILENCE_THRESHOLD:
                        has_speech = True
                        silent_frames = 0
                    elif has_speech:
                        silent_frames += 1
                        if silent_frames >= required_silent_frames:
                            break
                except queue.Empty:
                    break

        if not has_speech or not frames:
            return None

        audio_data = np.concatenate(frames, axis=0).flatten()
        result = self.whisper_model.transcribe(audio_data, fp16=False, language="en")
        text = result["text"].strip()

        if text:
            print(f"You: {text}")
        return text if text else None

    def get_ai_response(self, user_message: str) -> str:
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.conversation_history

        response = ollama.chat(
            model="llama3.2:3b",
            messages=messages,
        )

        assistant_message = response["message"]["content"]
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    def run(self):
        self.speak("Hey! I'm your offline AI assistant. How can I help you today?")

        while True:
            user_input = self.listen()

            if not user_input:
                continue

            if any(word in user_input.lower() for word in ["exit", "quit", "bye", "goodbye", "stop"]):
                self.speak("Goodbye! Have a great day!")
                break

            try:
                response = self.get_ai_response(user_input)
                self.speak(response)
            except Exception as e:
                print(f"Error: {e}")
                self.speak("Sorry, something went wrong. Please try again.")


def main():
    print("=" * 50)
    print("   Offline AI Voice Assistant (No API needed)")
    print("=" * 50)
    print("Say 'exit', 'quit', or 'bye' to stop.\n")

    assistant = VoiceAssistant()
    assistant.run()


if __name__ == "__main__":
    main()
