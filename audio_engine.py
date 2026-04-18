import numpy as np
import sounddevice as sd
import soundfile as sf
import os
import scipy.signal as signal

class AudioEngine:
    def __init__(self):
        self.audio_data = None
        self.sample_rate = 44100
        self.channels = 2
        
        self.position = 0.0
        self.is_playing = False
        self.volume = 0.5
        self.stream = None
        
        # DSP Effects parameters
        self.speed = 1.0
        self.bass_level = 0.0 # bounds -5 to 5
        self.reverb_level = 0.0 # bounds 0 to 1
        
        self.filter_zi = None
        
        self.delay_length = 0
        self.delay_buffer = None
        self.delay_pos = 0

    def load_track(self, file_path):
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False
            
        self.stop_audio()
        try:
            self.audio_data, self.sample_rate = sf.read(file_path, dtype='float32')
            if len(self.audio_data.shape) == 1:
                self.audio_data = np.column_stack((self.audio_data, self.audio_data))
            self.position = 0.0
            
            # Reset DSP buffers
            self.filter_zi = np.zeros((1, self.channels))
            self.delay_length = int(0.3 * self.sample_rate) # 300ms delay
            self.delay_buffer = np.zeros((self.delay_length, self.channels), dtype='float32')
            self.delay_pos = 0
            
            return True
        except Exception as e:
            print(f"Error loading audio: {e}")
            return False

    def trigger_play_pause(self):
        if self.audio_data is None:
            return
            
        if self.is_playing:
            self.is_playing = False
        else:
            self.is_playing = True
            if self.stream is None or not self.stream.active:
                self.stream = sd.OutputStream(
                    samplerate=self.sample_rate, 
                    channels=self.channels,
                    callback=self._audio_callback,
                    blocksize=2048
                )
                self.stream.start()
                
    def stop_audio(self):
        self.is_playing = False
        self.position = 0.0
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    def set_volume(self, target_volume):
        self.volume = max(0.0, min(1.0, target_volume))

    def set_dsp_effects(self, speed, bass, reverb):
        self.speed = max(0.5, min(2.0, speed))
        self.bass_level = max(-5.0, min(5.0, bass))
        self.reverb_level = max(0.0, min(1.0, reverb))

    def jump_time(self, seconds):
        if self.audio_data is not None:
            self.position += seconds * self.sample_rate
            self.position = max(0.0, min(float(len(self.audio_data) - 1), self.position))

    def _audio_callback(self, outdata, frames, time, status):
        outdata.fill(0)
        if not self.is_playing or self.audio_data is None:
            return
            
        max_idx = self.audio_data.shape[0] - 1
        
        # 1. SPEED & PITCH SHIFT (Vectorized nearest-neighbor resampling)
        idx = np.arange(frames) * self.speed + self.position
        
        if np.any(idx > max_idx):
            valid_frames = int(max_idx - self.position)
            if valid_frames <= 0:
                self.is_playing = False
                return
            valid_idx = idx[idx <= max_idx]
            raw_block = self.audio_data[valid_idx.astype(int)] * (self.volume ** 2)
            # Pad with zeros if we hit end of track
            raw_block = np.pad(raw_block, ((0, frames - len(raw_block)), (0, 0)), mode='constant')
            self.is_playing = False # Track finished 
        else:
            raw_block = self.audio_data[idx.astype(int)] * (self.volume ** 2)

        self.position += frames * self.speed
        
        # 2. BASS CONTROL (Real-time DSP Low-pass EQ)
        # Maps -5 (200Hz, muddy bass) to 0 (5000Hz, mid) to +5 (20000Hz, passthrough)
        cutoff = np.interp(self.bass_level, [-5, 0, 5], [200, 5000, 20000])
        b, a = signal.butter(1, cutoff, btype='low', fs=self.sample_rate)
        
        filtered_block, self.filter_zi = signal.lfilter(b, a, raw_block, axis=0, zi=self.filter_zi)
        
        # 3. REVERB / ECHO (Delay Ring Buffer)
        if self.delay_buffer is not None:
            end_d = self.delay_pos + frames
            if end_d <= self.delay_length:
                echo_block = self.delay_buffer[self.delay_pos : end_d]
                out_block = filtered_block + self.reverb_level * echo_block
                self.delay_buffer[self.delay_pos : end_d] = out_block
            else:
                rem = self.delay_length - self.delay_pos
                echo_block = np.vstack((self.delay_buffer[self.delay_pos:], self.delay_buffer[:frames - rem]))
                out_block = filtered_block + self.reverb_level * echo_block
                self.delay_buffer[self.delay_pos:] = out_block[:rem]
                self.delay_buffer[:frames - rem] = out_block[rem:]
                
            self.delay_pos = (self.delay_pos + frames) % self.delay_length
        else:
            out_block = filtered_block

        # Mix and prevent clipping
        outdata[:frames] = np.clip(out_block, -1.0, 1.0)
