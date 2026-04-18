import time
import numpy as np
import soundfile as sf
from audio_engine import AudioEngine

def create_test_wav(filename="test.wav"):
    sample_rate = 44100
    t = np.linspace(0, 5, sample_rate * 5)
    audio = 0.5 * np.sin(2 * np.pi * 440 * t)
    sf.write(filename, audio, sample_rate)

def test_audio():
    create_test_wav("test.wav")
    audio = AudioEngine()
    print("Loading track...")
    success = audio.load_track("test.wav") 
    print(f"Loaded: {success}")
    if success:
        audio.trigger_play_pause()
        print("Playing normal...")
        time.sleep(1)
        
        print("Playing fast (1.5x) with Reverb...")
        audio.set_dsp_effects(1.5, 5, 0.5)
        time.sleep(1)
        
        print("Playing slow (0.5x) with heavy bass (lowpass)...")
        audio.set_dsp_effects(0.5, -4, 0.0)
        time.sleep(1)
        
        audio.stop_audio()
        print("Stopped.")

if __name__ == "__main__":
    test_audio()

