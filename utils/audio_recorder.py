import tempfile
import os
import wave
import threading
import time
from datetime import datetime
from typing import List, Dict, Optional, Any
import streamlit as st

# Try to import audio libraries - graceful fallback if not available
try:
    import sounddevice as sd
    import numpy as np
    AUDIO_AVAILABLE = True
except (ImportError, OSError) as e:
    AUDIO_AVAILABLE = False
    # Type stubs for when libraries are not available
    sd = None  # type: ignore
    np = None  # type: ignore
    st.warning(f"🎙️ Direct microphone recording not available in this environment: {e}")
    st.info("💡 Use the Virtual Meeting integration methods instead!")

class AudioRecorder:
    """Handle real-time audio recording from microphone"""
    
    def __init__(self, sample_rate=16000, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.recording = False
        self.audio_data = []
        self.stream = None
        self.temp_file = None
        
    def get_audio_devices(self) -> List[Dict[str, Any]]:
        """Get list of available audio input devices"""
        if not AUDIO_AVAILABLE or sd is None:
            return []
            
        try:
            if sd is None:
                return []
            devices = sd.query_devices()
            input_devices = []
            
            for i, device in enumerate(devices):
                # Check if device has input capabilities
                max_inputs = getattr(device, 'max_input_channels', 0)
                if max_inputs and max_inputs > 0:
                    device_name = getattr(device, 'name', f'Device {i}')
                    default_sr = getattr(device, 'default_samplerate', 44100)
                    
                    input_devices.append({
                        'index': i,
                        'name': str(device_name),
                        'channels': int(max_inputs),
                        'sample_rate': int(default_sr)
                    })
            
            return input_devices
        except Exception as e:
            st.error(f"Error getting audio devices: {e}")
            return []
    
    def start_recording(self, device_id=None) -> bool:
        """Start recording audio from microphone"""
        if not AUDIO_AVAILABLE or sd is None:
            st.error("Audio recording not available in this environment")
            return False
            
        if self.recording:
            return False
        
        try:
            self.audio_data = []
            self.recording = True
            
            def audio_callback(indata, frames, time, status):
                if status:
                    st.warning(f"Audio recording status: {status}")
                if self.recording:
                    self.audio_data.append(indata.copy())
            
            # Start the audio stream
            if np is None or sd is None:
                st.error("Audio libraries not available for audio processing")
                return False
                
            self.stream = sd.InputStream(
                device=device_id,
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=audio_callback,
                dtype=np.float32
            )
            
            self.stream.start()
            return True
            
        except Exception as e:
            st.error(f"Error starting recording: {e}")
            self.recording = False
            return False
    
    def stop_recording(self) -> Optional[str]:
        """Stop recording and save to temporary file"""
        if not self.recording:
            return None
        
        try:
            self.recording = False
            
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None
            
            if not self.audio_data:
                return None
            
            if not AUDIO_AVAILABLE or np is None:
                return None
                
            # Combine all audio chunks
            audio_array = np.concatenate(self.audio_data, axis=0)
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            self.temp_file = temp_file.name
            temp_file.close()
            
            # Save as WAV file
            with wave.open(self.temp_file, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.sample_rate)
                
                # Convert float32 to int16
                audio_int16 = (audio_array * 32767).astype(np.int16)
                wf.writeframes(audio_int16.tobytes())
            
            return self.temp_file
            
        except Exception as e:
            st.error(f"Error stopping recording: {e}")
            return None
    
    def get_recording_duration(self):
        """Get current recording duration in seconds"""
        if not self.recording or not self.audio_data:
            return 0
        
        total_frames = sum(len(chunk) for chunk in self.audio_data)
        return total_frames / self.sample_rate
    
    def cleanup(self):
        """Clean up temporary files"""
        if self.temp_file and os.path.exists(self.temp_file):
            try:
                os.unlink(self.temp_file)
                self.temp_file = None
            except Exception as e:
                st.warning(f"Could not delete temporary file: {e}")
    
    def is_recording(self):
        """Check if currently recording"""
        return self.recording

class SystemAudioCapture:
    """Handle system audio capture for virtual meetings"""
    
    def __init__(self):
        self.recording = False
        self.audio_data = []
        
    def get_system_audio_devices(self) -> List[Dict[str, Any]]:
        """Get system audio output devices that can be captured"""
        if not AUDIO_AVAILABLE or sd is None:
            return []
            
        try:
            if sd is None:
                return []
            devices = sd.query_devices()
            output_devices = []
            
            for i, device in enumerate(devices):
                # Check if device has output capabilities
                max_outputs = getattr(device, 'max_output_channels', 0)
                if max_outputs and max_outputs > 0:
                    device_name = getattr(device, 'name', f'Device {i}')
                    default_sr = getattr(device, 'default_samplerate', 44100)
                    
                    # Look for loopback or monitor devices
                    device_name_str = str(device_name)
                    if any(keyword in device_name_str.lower() for keyword in ['loopback', 'monitor', 'stereo mix', 'what u hear']):
                        output_devices.append({
                            'index': i,
                            'name': device_name_str,
                            'channels': int(max_outputs),
                            'sample_rate': int(default_sr)
                        })
            
            return output_devices
        except Exception as e:
            st.error(f"Error getting system audio devices: {e}")
            return []
    
    def start_system_capture(self, device_id=None):
        """Start capturing system audio"""
        # Implementation would depend on the operating system
        # This is a placeholder for system audio capture
        st.info("System audio capture requires additional system configuration.")
        st.info("For Windows: Enable 'Stereo Mix' in Recording devices")
        st.info("For macOS: Use tools like BlackHole or SoundFlower")
        st.info("For Linux: Use PulseAudio loopback module")
        return False

class BrowserAudioRecorder:
    """Handle browser-based audio recording using JavaScript"""
    
    @staticmethod
    def create_audio_recorder_component():
        """Create a custom audio recording component"""
        # This would require a custom Streamlit component
        # For now, we'll provide instructions for browser-based recording
        
        html_code = """
        <div style="border: 2px dashed #ccc; padding: 20px; text-align: center; margin: 10px 0;">
            <h4>🎙️ Browser Audio Recording</h4>
            <p>For browser-based recording, you can:</p>
            <ul style="text-align: left; display: inline-block;">
                <li>Use browser extensions like "Audio Recorder" or "Voice Recorder"</li>
                <li>Use online tools that integrate with your meeting platform</li>
                <li>Record directly in Zoom/Teams/Meet using built-in recording features</li>
            </ul>
            <p><em>Then upload the recorded file using the file uploader above.</em></p>
        </div>
        """
        
        return html_code

def get_recording_instructions():
    """Get instructions for different recording methods"""
    return {
        'microphone': {
            'title': '🎙️ Direct Microphone Recording',
            'description': 'Record directly from your microphone in real-time',
            'pros': ['Real-time processing', 'Privacy-first', 'No file management'],
            'cons': ['Only captures your voice', 'Background noise'],
            'best_for': 'Personal notes, interviews, voice memos'
        },
        'system_audio': {
            'title': '🔊 System Audio Capture',
            'description': 'Capture all audio playing on your computer',
            'pros': ['Captures meeting participants', 'High quality', 'No echo'],
            'cons': ['Complex setup', 'OS-dependent', 'Privacy concerns'],
            'best_for': 'Virtual meetings, presentations, webinars'
        },
        'browser_recording': {
            'title': '🌐 Browser-Based Recording',
            'description': 'Use browser extensions or online tools',
            'pros': ['Easy setup', 'Works with all platforms', 'Cloud backup'],
            'cons': ['Requires extensions', 'Internet dependent', 'Third-party tools'],
            'best_for': 'Quick recordings, cross-platform compatibility'
        },
        'meeting_platform': {
            'title': '📹 Meeting Platform Recording',
            'description': 'Use built-in recording features of Zoom/Teams/Meet',
            'pros': ['Native integration', 'High quality', 'Automatic transcripts'],
            'cons': ['Platform-specific', 'Requires permissions', 'Cloud storage'],
            'best_for': 'Formal meetings, team collaborations'
        }
    }