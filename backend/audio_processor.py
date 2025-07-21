import whisper
import os
import tempfile
import time
import numpy as np
from typing import Optional
import io

class AudioProcessor:
    def __init__(self):
        """Initialize Whisper model"""
        print("Loading Whisper model...")
        self.model = whisper.load_model("base")
        print("Whisper model loaded successfully")
        
        # Try to load audio processing libraries
        try:
            import librosa
            self.use_librosa = True
            print("Using librosa for audio processing")
        except ImportError:
            self.use_librosa = False
            print("librosa not available, using whisper's built-in audio loading")
    
    def load_audio_with_librosa(self, file_path: str) -> Optional[np.ndarray]:
        """Load audio using librosa (doesn't need ffmpeg)"""
        try:
            import librosa
            # Load audio with librosa (default sample rate is 22050, whisper expects 16000)
            audio, sr = librosa.load(file_path, sr=16000, dtype=np.float32)
            # Ensure it's float32 for whisper compatibility
            audio = audio.astype(np.float32)
            return audio
        except Exception as e:
            print(f"Error loading audio with librosa: {e}")
            return None
    
    def load_audio_bytes_with_librosa(self, audio_bytes: bytes) -> Optional[np.ndarray]:
        """Load audio from bytes using librosa"""
        try:
            import librosa
            import soundfile as sf
            
            # Create a BytesIO object
            audio_buffer = io.BytesIO(audio_bytes)
            
            # Try to read with soundfile first
            try:
                audio, sr = sf.read(audio_buffer, dtype='float32')
                # Ensure it's 1D array
                if len(audio.shape) > 1:
                    audio = audio.mean(axis=1)  # Convert stereo to mono
                # Resample to 16kHz if needed
                if sr != 16000:
                    audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
                # Ensure float32 type
                audio = audio.astype(np.float32)
                print(f"Loaded audio: shape={audio.shape}, dtype={audio.dtype}, sample_rate=16000")
                return audio
            except Exception as sf_error:
                print(f"Soundfile reading failed: {sf_error}")
                # Reset buffer position
                audio_buffer.seek(0)
                # Try with librosa directly
                audio, sr = librosa.load(audio_buffer, sr=16000, dtype=np.float32)
                # Ensure float32 type
                audio = audio.astype(np.float32)
                print(f"Loaded audio with librosa: shape={audio.shape}, dtype={audio.dtype}")
                return audio
                
        except Exception as e:
            print(f"Error loading audio bytes with librosa: {e}")
            return None
   
    def transcribe_audio(self, audio_file_path: str) -> Optional[str]:
        """Transcribe audio file to text using Whisper"""
        try:
            if not os.path.exists(audio_file_path):
                print(f"Audio file not found: {audio_file_path}")
                return None
           
            print(f"Transcribing audio file: {audio_file_path}")
            
            # Check file size
            file_size = os.path.getsize(audio_file_path)
            print(f"Audio file size: {file_size} bytes")
            
            if file_size == 0:
                print("Audio file is empty")
                return None
            
            # Try loading with librosa first (doesn't need ffmpeg)
            if self.use_librosa:
                audio_array = self.load_audio_with_librosa(audio_file_path)
                if audio_array is not None:
                    result = self.model.transcribe(audio_array)
                else:
                    # Fallback to whisper's built-in loading
                    result = self.model.transcribe(audio_file_path)
            else:
                # Use whisper's built-in loading (needs ffmpeg)
                result = self.model.transcribe(audio_file_path)
           
            # Extract the text
            transcribed_text = result["text"].strip()
           
            # Get detected language
            detected_language = result.get("language", "unknown")
           
            print(f"Transcription successful. Language: {detected_language}")
            print(f"Transcribed text: {transcribed_text}")
           
            return transcribed_text
           
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            import traceback
            traceback.print_exc()
            return None
   
    def transcribe_audio_bytes(self, audio_bytes: bytes, filename: str = "audio.ogg") -> Optional[str]:
        """Transcribe audio from bytes"""
        try:
            print(f"Processing {len(audio_bytes)} bytes of audio data")
            
            if len(audio_bytes) == 0:
                print("No audio data received")
                return None
            
            # Try direct processing with librosa (no temp file needed)
            if self.use_librosa:
                print("Attempting direct audio processing with librosa...")
                audio_array = self.load_audio_bytes_with_librosa(audio_bytes)
                if audio_array is not None:
                    print(f"Audio loaded successfully: shape={audio_array.shape}, dtype={audio_array.dtype}")
                    
                    # Ensure the audio array is properly formatted for whisper
                    if len(audio_array.shape) > 1:
                        audio_array = audio_array.flatten()
                    
                    # Ensure it's float32
                    audio_array = audio_array.astype(np.float32)
                    
                    # Normalize audio if needed
                    if np.max(np.abs(audio_array)) > 1.0:
                        audio_array = audio_array / np.max(np.abs(audio_array))
                    
                    print(f"Processing audio with whisper: shape={audio_array.shape}, dtype={audio_array.dtype}, max={np.max(audio_array):.3f}")
                    
                    result = self.model.transcribe(audio_array)
                    transcribed_text = result["text"].strip()
                    print(f"Direct transcription successful: {transcribed_text}")
                    return transcribed_text
            
            # Fallback to temp file approach
            print("Falling back to temporary file approach...")
            return self.transcribe_with_temp_file(audio_bytes, filename)
           
        except Exception as e:
            print(f"Error transcribing audio bytes: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def transcribe_with_temp_file(self, audio_bytes: bytes, filename: str) -> Optional[str]:
        """Fallback method using temporary file"""
        temp_path = None
        try:
            # Create a unique temporary file path
            timestamp = str(int(time.time() * 1000))
            temp_dir = tempfile.gettempdir()
            
            # Get file extension
            file_ext = os.path.splitext(filename)[1] if filename else '.ogg'
            if not file_ext:
                file_ext = '.ogg'
            
            # Create temp file path
            temp_path = os.path.join(temp_dir, f"whisper_audio_{timestamp}{file_ext}")
            
            print(f"Creating temporary file: {temp_path}")
            
            # Write audio bytes to file
            with open(temp_path, 'wb') as f:
                f.write(audio_bytes)
            
            # Verify file was created and has content
            if not os.path.exists(temp_path):
                print(f"Failed to create temporary file: {temp_path}")
                return None
                
            file_size = os.path.getsize(temp_path)
            print(f"Temporary file created successfully: {temp_path} ({file_size} bytes)")
            
            if file_size == 0:
                print("Temporary file is empty")
                return None
            
            # Small delay to ensure file is fully written
            time.sleep(0.1)
           
            # Transcribe the temporary file
            result = self.transcribe_audio(temp_path)
           
            return result
           
        except Exception as e:
            print(f"Error in temp file transcription: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            # Clean up temporary file
            if temp_path and os.path.exists(temp_path):
                try:
                    time.sleep(0.1)
                    os.remove(temp_path)
                    print(f"Cleaned up temporary file: {temp_path}")
                except Exception as cleanup_error:
                    print(f"Warning: Could not clean up temporary file {temp_path}: {cleanup_error}")