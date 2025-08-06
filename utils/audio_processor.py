import os
from pydub import AudioSegment
import streamlit as st

class AudioProcessor:
    """Handle audio file processing and conversion"""
    
    def __init__(self):
        self.supported_formats = ['wav', 'mp3', 'mp4', 'm4a', 'flac', 'ogg']
    
    def process_audio(self, file_path):
        """
        Process audio file and return metadata
        
        Args:
            file_path (str): Path to audio file
            
        Returns:
            dict: Audio metadata including duration and file size
        """
        try:
            # Load audio file
            audio = AudioSegment.from_file(file_path)
            
            # Get metadata
            duration_ms = len(audio)
            duration_minutes = duration_ms / (1000 * 60)
            
            # Get file size in MB
            file_size_bytes = os.path.getsize(file_path)
            file_size_mb = file_size_bytes / (1024 * 1024)
            
            # Convert to WAV for better Whisper compatibility if needed
            if not file_path.lower().endswith('.wav'):
                wav_path = file_path.replace(file_path.split('.')[-1], 'wav')
                audio.export(wav_path, format="wav")
                
                # Update file path for transcription
                if os.path.exists(wav_path):
                    os.rename(wav_path, file_path + '.wav')
                    file_path = file_path + '.wav'
            
            return {
                'duration': duration_minutes,
                'file_size': file_size_mb,
                'sample_rate': audio.frame_rate,
                'channels': audio.channels,
                'format': 'wav',
                'processed_path': file_path
            }
            
        except Exception as e:
            raise Exception(f"Error processing audio file: {str(e)}")
    
    def validate_audio_file(self, file_path):
        """
        Validate if the audio file is supported and processable
        
        Args:
            file_path (str): Path to audio file
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Check file extension
            file_ext = file_path.split('.')[-1].lower()
            if file_ext not in self.supported_formats:
                return False
            
            # Try to load the file
            audio = AudioSegment.from_file(file_path)
            
            # Check if audio has content
            if len(audio) == 0:
                return False
            
            # Check minimum duration (1 second)
            if len(audio) < 1000:
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_audio_info(self, file_path):
        """
        Get basic audio file information without processing
        
        Args:
            file_path (str): Path to audio file
            
        Returns:
            dict: Basic audio information
        """
        try:
            audio = AudioSegment.from_file(file_path)
            
            return {
                'duration_seconds': len(audio) / 1000,
                'duration_minutes': len(audio) / (1000 * 60),
                'sample_rate': audio.frame_rate,
                'channels': audio.channels,
                'format': file_path.split('.')[-1].lower()
            }
            
        except Exception as e:
            return {
                'error': f"Could not read audio file: {str(e)}"
            }
