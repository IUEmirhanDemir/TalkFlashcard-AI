import sounddevice as sd
import soundfile as sf
import os

def test_microphone(record_seconds=5, filename="./test_recorded.wav"):
    fs = 16000
    channels = 1

    print("Starte Aufnahme...")
    recording = sd.rec(int(record_seconds * fs), samplerate=fs, channels=channels, dtype='int16')
    sd.wait()
    print("Aufnahme beendet.")

    os.makedirs(os.path.dirname(filename), exist_ok=True)

    sf.write(filename, recording, fs)
    print(f"Audio gespeichert unter: {filename}")

if __name__ == "__main__":
    test_microphone()
