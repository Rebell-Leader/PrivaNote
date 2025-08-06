import os
import tempfile
from faster_whisper import WhisperModel
import streamlit as st

class TranscriptionService:
    """Handle local audio transcription using faster-whisper"""
    
    def __init__(self):
        self.model = None
        self.model_size = "base"  # Start with base model for speed/accuracy balance
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the Whisper model"""
        try:
            # Use CPU for broader compatibility, GPU if available
            device = "auto"  # Let faster-whisper decide
            compute_type = "float16" if device != "cpu" else "int8"
            
            # Initialize model with caching
            self.model = WhisperModel(
                self.model_size, 
                device=device, 
                compute_type=compute_type,
                download_root=None  # Use default cache directory
            )
            
        except Exception as e:
            st.error(f"Error initializing Whisper model: {str(e)}")
            self.model = None
    
    def transcribe(self, audio_path, language=None):
        """
        Transcribe audio file to text
        
        Args:
            audio_path (str): Path to audio file
            language (str, optional): Language code for transcription
            
        Returns:
            str: Transcribed text
        """
        if not self.model:
            raise Exception("Whisper model not initialized")
        
        try:
            # Transcribe with faster-whisper
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                beam_size=5,
                best_of=5,
                temperature=0.0,
                condition_on_previous_text=False,
                initial_prompt=None,
                word_timestamps=False,
                vad_filter=True,  # Voice activity detection
                vad_parameters=dict(
                    min_silence_duration_ms=500,
                    speech_pad_ms=400
                )
            )
            
            # Combine all segments into full transcript
            transcript_text = ""
            for segment in segments:
                transcript_text += segment.text.strip() + " "
            
            # Clean up the transcript
            transcript_text = self._clean_transcript(transcript_text.strip())
            
            if not transcript_text:
                raise Exception("No speech detected in audio")
            
            return transcript_text
            
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")
    
    def transcribe_with_timestamps(self, audio_path, language=None):
        """
        Transcribe audio with timestamp information
        
        Args:
            audio_path (str): Path to audio file
            language (str, optional): Language code for transcription
            
        Returns:
            list: List of segments with timestamps
        """
        if not self.model:
            raise Exception("Whisper model not initialized")
        
        try:
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                beam_size=5,
                best_of=5,
                temperature=0.0,
                word_timestamps=True,
                vad_filter=True
            )
            
            timestamped_segments = []
            for segment in segments:
                timestamped_segments.append({
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text.strip(),
                    'duration': segment.end - segment.start
                })
            
            return timestamped_segments
            
        except Exception as e:
            raise Exception(f"Timestamped transcription failed: {str(e)}")
    
    def _clean_transcript(self, text):
        """
        Clean and normalize transcript text
        
        Args:
            text (str): Raw transcript text
            
        Returns:
            str: Cleaned transcript text
        """
        if not text:
            return ""
        
        # Basic cleanup
        text = text.strip()
        
        # Remove multiple spaces
        import re
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common transcription issues
        text = text.replace(' .', '.')
        text = text.replace(' ,', ',')
        text = text.replace(' ?', '?')
        text = text.replace(' !', '!')
        
        # Ensure sentences start with capital letters
        sentences = text.split('. ')
        cleaned_sentences = []
        for sentence in sentences:
            if sentence:
                sentence = sentence.strip()
                if sentence:
                    sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
                    cleaned_sentences.append(sentence)
        
        text = '. '.join(cleaned_sentences)
        
        # Ensure text ends with punctuation
        if text and text[-1] not in '.!?':
            text += '.'
        
        return text
    
    def get_supported_languages(self):
        """Get list of supported languages"""
        return [
            "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh",
            "ar", "hi", "tr", "pl", "nl", "sv", "da", "no", "fi"
        ]
    
    def change_model_size(self, size):
        """
        Change the Whisper model size
        
        Args:
            size (str): Model size (tiny, base, small, medium, large)
        """
        valid_sizes = ["tiny", "base", "small", "medium", "large"]
        if size not in valid_sizes:
            raise ValueError(f"Invalid model size. Choose from: {valid_sizes}")
        
        if size != self.model_size:
            self.model_size = size
            self._initialize_model()
    
    def get_model_info(self):
        """Get current model information"""
        return {
            'size': self.model_size,
            'initialized': self.model is not None,
            'supported_languages': self.get_supported_languages()
        }
