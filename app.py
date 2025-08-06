import streamlit as st
import os
import tempfile
import time
from datetime import datetime

from utils.audio_processor import AudioProcessor
from utils.transcription import TranscriptionService
from utils.ai_analysis import AIAnalysisService
from utils.storage import StorageService
from utils.export import ExportService
from utils.audio_recorder import AudioRecorder, get_recording_instructions

# Page configuration
st.set_page_config(
    page_title="PrivaNote - Privacy-First Meeting Assistant",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
@st.cache_resource
def get_services():
    return {
        'audio': AudioProcessor(),
        'transcription': TranscriptionService(),
        'storage': StorageService(),
        'export': ExportService()
    }

# Initialize cached services
services = get_services()

# Initialize AI service separately for provider switching
if 'ai_provider' not in st.session_state:
    st.session_state.ai_provider = 'openai'
if 'ai_model' not in st.session_state:
    st.session_state.ai_model = 'gpt-4o'
if 'lm_studio_config' not in st.session_state:
    st.session_state.lm_studio_config = {'host': 'localhost', 'port': 1234, 'model': 'google/gemma-3n-e4b'}

# Initialize session state
if 'meetings' not in st.session_state:
    st.session_state.meetings = []
if 'current_meeting' not in st.session_state:
    st.session_state.current_meeting = None
if 'audio_recorder' not in st.session_state:
    st.session_state.audio_recorder = None
if 'recording_file' not in st.session_state:
    st.session_state.recording_file = None

def main():
    # Header
    st.title("🔒 PrivaNote")
    st.markdown("**Privacy-First AI Meeting Assistant** - Local transcription and intelligent analysis")
    
    # Privacy notice
    with st.expander("🛡️ Privacy & Security Information", expanded=False):
        st.markdown("""
        **Your Privacy is Our Priority:**
        - ✅ **Audio transcription**: Processed locally using Whisper
        - ✅ **Data storage**: All meeting data stored locally in your browser
        - 🔄 **AI analysis**: Choose between OpenAI (cloud) or local Gemma models
        - ✅ **Audio privacy**: No audio files sent to external services
        - ✅ **No tracking**: No persistent server-side storage
        - ⚠️ **Data removal**: Clear browser data to remove all stored meetings
        """)
    
    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        tab = st.radio(
            "Select Function:",
            ["📤 Upload & Analyze", "🎙️ Live Recording", "📋 Meeting Archive", "🔍 Search Meetings"],
            index=0
        )
        
        st.markdown("---")
        
        # AI Provider Selection
        st.markdown("### AI Configuration")
        
        # Initialize AI service if not exists
        if 'ai_service' not in st.session_state:
            st.session_state.ai_service = AIAnalysisService(
                provider=st.session_state.ai_provider,
                model_name=st.session_state.ai_model,
                lm_studio_config=st.session_state.lm_studio_config
            )
        
        # Get available providers
        available_providers = st.session_state.ai_service.get_available_providers()
        
        # Always show provider selector with all possible options
        all_provider_options = [
            {
                'name': 'OpenAI (Cloud) ☁️',
                'value': 'openai',
                'available': any(p['value'] == 'openai' for p in available_providers),
                'description': 'High-quality analysis via OpenAI API',
                'privacy': 'Transcript sent to OpenAI'
            },
            {
                'name': 'Local Gemma (Ollama) 🏠',
                'value': 'ollama', 
                'available': any(p['value'] == 'ollama' for p in available_providers),
                'description': 'Fully private local processing',
                'privacy': 'Data never leaves your device'
            },
            {
                'name': 'LM Studio (Local Server) 🖥️',
                'value': 'lm_studio',
                'available': any(p['value'] == 'lm_studio' for p in available_providers),
                'description': 'OpenAI-compatible local server',
                'privacy': 'Data processed on local LM Studio server'
            },
            {
                'name': 'Basic Analysis (No AI) 🔧',
                'value': 'fallback',
                'available': True,
                'description': 'Simple keyword-based analysis',
                'privacy': 'Fully local'
            }
        ]
        
        # Create display options with status indicators
        provider_display_options = []
        provider_value_map = {}
        
        for option in all_provider_options:
            if option['available']:
                display_name = option['name']
            else:
                display_name = f"{option['name']} (Setup Required)"
                
            provider_display_options.append(display_name)
            provider_value_map[display_name] = option
        
        # Find current selection
        current_option = next(
            (opt for opt in all_provider_options if opt['value'] == st.session_state.ai_provider),
            all_provider_options[0]
        )
        
        current_display_name = next(
            (name for name, opt in provider_value_map.items() if opt['value'] == current_option['value']),
            provider_display_options[0]
        )
        
        # Provider selector (always visible)
        selected_display_name = st.selectbox(
            "AI Provider",
            options=provider_display_options,
            index=provider_display_options.index(current_display_name),
            help="Choose your preferred AI processing method"
        )
        
        selected_option = provider_value_map[selected_display_name]
        
        # Handle provider selection
        if selected_option['available'] and selected_option['value'] != st.session_state.ai_provider:
            st.session_state.ai_provider = selected_option['value']
            st.session_state.ai_service = AIAnalysisService(
                provider=selected_option['value'],
                model_name=st.session_state.ai_model,
                lm_studio_config=st.session_state.lm_studio_config
            )
            st.rerun()
        
        # Show provider info and setup instructions
        if selected_option['available']:
            st.success(
                f"✅ **{selected_option['name'].split(' (')[0]}** - Ready\n\n"
                f"{selected_option['description']}\n\n"
                f"🔒 Privacy: {selected_option['privacy']}"
            )
        elif selected_option['value'] == 'openai':
            st.warning(
                f"⚠️ **OpenAI (Cloud)** - Setup Required\n\n"
                f"{selected_option['description']}\n\n"
                f"🔒 Privacy: {selected_option['privacy']}\n\n"
                f"**Setup:** Add OpenAI API key in Replit Secrets"
            )
            if st.button("ℹ️ How to add OpenAI API Key", key="openai_help"):
                st.info("""
                **To enable OpenAI analysis:**
                1. Go to Replit Secrets (in sidebar)
                2. Add key: `OPENAI_API_KEY`
                3. Add your OpenAI API key as value
                4. Restart the app
                """)
        elif selected_option['value'] == 'ollama':
            st.info(
                f"🏠 **Local Gemma (Ollama)** - Setup Required\n\n"
                f"{selected_option['description']}\n\n"
                f"🔒 Privacy: {selected_option['privacy']}\n\n"
                f"**Setup:** Install Ollama locally (see Privacy section)"
            )
            if st.button("🏠 How to setup Local Ollama", key="ollama_help"):
                st.info("""
                **For maximum privacy with local processing:**
                1. Download this app's code
                2. Install Ollama locally from ollama.com
                3. Run: `ollama pull gemma3`
                4. Run this app locally with `streamlit run app.py`
                """)
        elif selected_option['value'] == 'lm_studio':
            st.warning(
                f"⚠️ **LM Studio (Local Server)** - Setup Required\n\n"
                f"{selected_option['description']}\n\n"
                f"🔒 Privacy: {selected_option['privacy']}\n\n"
                f"**Setup:** Configure and start LM Studio server"
            )
            
            # LM Studio Configuration
            st.markdown("**LM Studio Configuration:**")
            col1, col2 = st.columns(2)
            with col1:
                lm_host = st.text_input(
                    "Host/IP Address", 
                    value=st.session_state.lm_studio_config['host'],
                    help="LM Studio server IP address (e.g., localhost, 172.28.0.1)"
                )
            with col2:
                lm_port = st.number_input(
                    "Port", 
                    value=st.session_state.lm_studio_config['port'],
                    min_value=1000,
                    max_value=65535,
                    help="LM Studio server port (default: 1234)"
                )
            
            lm_model = st.text_input(
                "Model Name", 
                value=st.session_state.lm_studio_config['model'],
                help="LM Studio model name (e.g., google/gemma-3n-e4b)"
            )
            
            # Update configuration
            new_config = {'host': lm_host, 'port': lm_port, 'model': lm_model}
            if new_config != st.session_state.lm_studio_config:
                st.session_state.lm_studio_config = new_config
                st.session_state.ai_service = AIAnalysisService(
                    provider=st.session_state.ai_provider,
                    model_name=lm_model,
                    lm_studio_config=new_config
                )
                st.rerun()
            
            if st.button("🔄 Test Connection", key="lm_studio_test"):
                with st.spinner("Testing LM Studio connection..."):
                    test_service = AIAnalysisService(
                        provider='lm_studio',
                        model_name=lm_model,
                        lm_studio_config=new_config
                    )
                    if test_service.lm_studio_available:
                        st.success(f"✅ Connected to LM Studio at {lm_host}:{lm_port}")
                    else:
                        st.error(f"❌ Cannot connect to LM Studio at {lm_host}:{lm_port}")
            
            if st.button("ℹ️ How to setup LM Studio", key="lm_studio_help"):
                st.info("""
                **LM Studio Setup Instructions:**
                
                1. **Download LM Studio:**
                   - Visit: https://lmstudio.ai
                   - Download and install for your platform
                
                2. **Load a Gemma model:**
                   - In LM Studio, go to "Discover" tab
                   - Search for "gemma" and download a model
                   - Recommended: google/gemma-3n-e4b or similar
                
                3. **Start Local Server:**
                   - Go to "Local Server" tab in LM Studio
                   - Select your downloaded model
                   - Click "Start Server" (default port: 1234)
                
                4. **Configure PrivaNote:**
                   - Set Host/IP (localhost for same machine)
                   - Set Port (default: 1234)
                   - Set Model Name (e.g., google/gemma-3n-e4b)
                   - Click "Test Connection"
                """)
        
        
        st.markdown("---")
        st.markdown("### Quick Stats")
        total_meetings = len(st.session_state.meetings)
        st.metric("Total Meetings", total_meetings)
        
        if total_meetings > 0:
            total_duration = sum([m.get('duration', 0) for m in st.session_state.meetings])
            st.metric("Total Audio Time", f"{total_duration:.1f} min")
    
    # Main content area
    if tab == "📤 Upload & Analyze":
        upload_and_analyze_tab()
    elif tab == "🎙️ Live Recording":
        live_recording_tab()
    elif tab == "📋 Meeting Archive":
        meeting_archive_tab()
    else:
        search_meetings_tab()

def live_recording_tab():
    st.header("🎙️ Live Audio Recording")
    
    # Initialize audio recorder
    if st.session_state.audio_recorder is None:
        st.session_state.audio_recorder = AudioRecorder()
    
    recorder = st.session_state.audio_recorder
    
    # Recording method selection
    st.subheader("Choose Recording Method")
    
    method_tabs = st.tabs(["🎙️ Microphone", "🔊 System Audio", "🌐 Virtual Meetings", "ℹ️ Instructions"])
    
    with method_tabs[0]:
        microphone_recording_section(recorder)
    
    with method_tabs[1]:
        system_audio_section()
    
    with method_tabs[2]:
        virtual_meeting_section()
    
    with method_tabs[3]:
        recording_instructions_section()

def microphone_recording_section(recorder):
    st.markdown("### Direct Microphone Recording")
    st.info("🔒 **Privacy**: Audio is processed entirely on your device")
    
    # Check if audio is available
    from utils.audio_recorder import AUDIO_AVAILABLE
    if not AUDIO_AVAILABLE:
        st.warning("🎙️ Direct microphone recording is not available in this web environment.")
        st.info("""
        **Alternative options for recording:**
        
        1. **Use Virtual Meeting Platform Recording** (see Virtual Meetings tab)
        2. **Record locally and upload** using the Upload & Analyze tab
        3. **Use browser-based recording tools** and then upload the file
        """)
        return
    
    # Device selection
    devices = recorder.get_audio_devices()
    
    if not devices:
        st.error("❌ No audio input devices found. Please check your microphone connections.")
        return
    
    # Device selector
    device_options = [f"{device['name']} ({device['channels']} channels)" for device in devices]
    selected_device_idx = st.selectbox(
        "Select Microphone",
        range(len(device_options)),
        format_func=lambda x: device_options[x],
        help="Choose which microphone to record from"
    )
    
    selected_device = devices[selected_device_idx]
    
    # Display device info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Channels", selected_device['channels'])
    with col2:
        st.metric("Sample Rate", f"{selected_device['sample_rate']:.0f} Hz")
    with col3:
        if recorder.is_recording():
            st.metric("Duration", f"{recorder.get_recording_duration():.1f}s")
        else:
            st.metric("Status", "Ready")
    
    # Meeting metadata for recording
    col1, col2 = st.columns(2)
    with col1:
        meeting_title = st.text_input(
            "Meeting Title", 
            placeholder="e.g., Live Team Meeting",
            key="live_meeting_title"
        )
    with col2:
        meeting_date = st.date_input(
            "Meeting Date", 
            value=datetime.now().date(),
            key="live_meeting_date"
        )
    
    meeting_notes = st.text_area(
        "Notes (Optional)", 
        placeholder="Add context about this recording...",
        key="live_meeting_notes"
    )
    
    # Recording controls
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if not recorder.is_recording():
            if st.button("🔴 Start Recording", type="primary", disabled=not meeting_title):
                if recorder.start_recording(selected_device['index']):
                    st.success("🎙️ Recording started!")
                    st.rerun()
                else:
                    st.error("❌ Failed to start recording")
        else:
            if st.button("⏹️ Stop Recording", type="secondary"):
                audio_file = recorder.stop_recording()
                if audio_file:
                    st.session_state.recording_file = audio_file
                    st.success("✅ Recording stopped!")
                    st.rerun()
                else:
                    st.error("❌ Failed to stop recording")
    
    with col2:
        if recorder.is_recording():
            # Real-time duration display
            duration = recorder.get_recording_duration()
            st.markdown(f"**🔴 Recording: {duration:.1f}s**")
            
            # Auto-refresh every second while recording
            time.sleep(1)
            st.rerun()
    
    with col3:
        if not meeting_title:
            st.warning("⚠️ Please enter a meeting title to start recording")
    
    # Process recorded audio
    if st.session_state.recording_file and not recorder.is_recording():
        st.markdown("---")
        st.subheader("Process Recording")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Transcribe & Analyze", type="primary"):
                process_recorded_audio(
                    st.session_state.recording_file,
                    meeting_title,
                    meeting_date,
                    meeting_notes
                )
                
        with col2:
            if st.button("🗑️ Discard Recording"):
                recorder.cleanup()
                st.session_state.recording_file = None
                st.success("Recording discarded")
                st.rerun()

def system_audio_section():
    st.markdown("### System Audio Capture")
    st.info("🔊 **Capture**: All audio playing on your computer (including meeting participants)")
    
    st.warning("""
    **System audio capture requires additional setup:**
    
    **Windows:**
    - Enable "Stereo Mix" in Recording devices
    - Or use VB-Cable (Virtual Audio Cable)
    
    **macOS:**
    - Install BlackHole or SoundFlower
    - Configure as audio input device
    
    **Linux:**
    - Use PulseAudio monitor device
    - Configure loopback module
    """)
    
    if st.button("🔧 Try System Audio Capture (Experimental)"):
        st.info("This feature is under development. For now, please use:")
        st.markdown("""
        1. **Set your system to record system audio**
        2. **Use the microphone recording above**
        3. **Or record within your meeting platform and upload the file**
        """)

def virtual_meeting_section():
    st.markdown("### Virtual Meeting Integration")
    st.info("💬 **Integration**: Methods to capture audio from Zoom, Teams, Google Meet")
    
    # Meeting platform options
    platform_options = {
        "zoom": {
            "name": "Zoom",
            "icon": "🎥",
            "methods": [
                "Use Zoom's built-in recording feature",
                "Enable 'Record to this computer'",
                "Upload the recorded audio file"
            ]
        },
        "teams": {
            "name": "Microsoft Teams", 
            "icon": "💼",
            "methods": [
                "Use Teams recording feature",
                "Start recording during the meeting",
                "Download and upload the audio file"
            ]
        },
        "meet": {
            "name": "Google Meet",
            "icon": "🌐", 
            "methods": [
                "Use Google Meet recording (Google Workspace)",
                "Or use browser-based screen recording",
                "Upload the resulting audio file"
            ]
        },
        "general": {
            "name": "General Methods",
            "icon": "🛠️",
            "methods": [
                "Use OBS Studio to record system audio",
                "Use Audacity to record computer playback",
                "Use browser extensions for tab audio recording"
            ]
        }
    }
    
    selected_platform = st.selectbox(
        "Select Meeting Platform",
        options=list(platform_options.keys()),
        format_func=lambda x: f"{platform_options[x]['icon']} {platform_options[x]['name']}"
    )
    
    platform = platform_options[selected_platform]
    
    st.markdown(f"### {platform['icon']} {platform['name']} Recording")
    
    for i, method in enumerate(platform['methods'], 1):
        st.markdown(f"{i}. {method}")
    
    st.markdown("---")
    st.info("""
    **After recording with any platform:**
    1. Save/download the audio file
    2. Go to the "📤 Upload & Analyze" tab
    3. Upload your recorded file for analysis
    """)

def recording_instructions_section():
    st.markdown("### 📖 Recording Methods Guide")
    
    instructions = get_recording_instructions()
    
    for method_key, method_info in instructions.items():
        with st.expander(f"{method_info['title']}", expanded=False):
            st.markdown(f"**{method_info['description']}**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**✅ Pros:**")
                for pro in method_info['pros']:
                    st.markdown(f"• {pro}")
            
            with col2:
                st.markdown("**⚠️ Cons:**")
                for con in method_info['cons']:
                    st.markdown(f"• {con}")
            
            st.markdown(f"**🎯 Best for:** {method_info['best_for']}")

def process_recorded_audio(audio_file_path, title, date, notes):
    """Process audio recorded from microphone"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Process audio
        status_text.text("🎵 Processing recorded audio...")
        progress_bar.progress(20)
        
        audio_info = services['audio'].process_audio(audio_file_path)
        
        # Step 2: Transcribe
        status_text.text("🎯 Transcribing audio (this may take a while)...")
        progress_bar.progress(30)
        
        transcript = services['transcription'].transcribe(audio_file_path)
        progress_bar.progress(60)
        
        if not transcript or not transcript.strip():
            st.error("❌ No speech detected in the recording. Please check your microphone settings.")
            return
        
        # Step 3: AI Analysis
        status_text.text("🤖 Analyzing transcript with AI...")
        progress_bar.progress(70)
        
        analysis = st.session_state.ai_service.analyze_meeting(transcript)
        progress_bar.progress(90)
        
        # Step 4: Store meeting
        status_text.text("💾 Saving meeting data...")
        
        meeting_data = {
            'id': datetime.now().isoformat(),
            'title': title,
            'date': str(date),
            'notes': notes,
            'duration': audio_info['duration'],
            'file_size': audio_info['file_size'],
            'transcript': transcript,
            'analysis': analysis,
            'created_at': datetime.now().isoformat(),
            'source': 'live_recording'
        }
        
        services['storage'].save_meeting(meeting_data)
        progress_bar.progress(100)
        status_text.text("✅ Recording processed successfully!")
        
        # Clean up
        st.session_state.audio_recorder.cleanup()
        st.session_state.recording_file = None
        
        # Display results
        display_meeting_results(meeting_data)
        
        # Rerun to update sidebar stats
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error processing recording: {str(e)}")
        if st.session_state.audio_recorder:
            st.session_state.audio_recorder.cleanup()

def upload_and_analyze_tab():
    st.header("Upload Meeting Audio")
    
    # Get current AI service from session state
    ai_service = st.session_state.get('ai_service')
    if not ai_service:
        ai_service = AIAnalysisService()
        st.session_state.ai_service = ai_service
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=['wav', 'mp3', 'mp4', 'm4a', 'flac', 'ogg'],
        help="Supported formats: WAV, MP3, MP4, M4A, FLAC, OGG"
    )
    
    # Meeting metadata
    col1, col2 = st.columns(2)
    with col1:
        meeting_title = st.text_input("Meeting Title", placeholder="e.g., Weekly Team Standup")
    with col2:
        meeting_date = st.date_input("Meeting Date", value=datetime.now().date())
    
    meeting_notes = st.text_area("Additional Notes (Optional)", placeholder="Any context or notes about this meeting...")
    
    if uploaded_file is not None and meeting_title:
        if st.button("🚀 Process Meeting", type="primary"):
            process_meeting(uploaded_file, meeting_title, meeting_date, meeting_notes)

def process_meeting(uploaded_file, title, date, notes):
    progress_bar = st.progress(0)
    status_text = st.empty()
    temp_path = None  # Initialize temp_path
    
    try:
        # Step 1: Save uploaded file
        status_text.text("📁 Saving audio file...")
        progress_bar.progress(10)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.read())
            temp_path = tmp_file.name
        
        # Step 2: Process audio
        status_text.text("🎵 Processing audio...")
        progress_bar.progress(20)
        
        audio_info = services['audio'].process_audio(temp_path)
        
        # Step 3: Transcribe
        status_text.text("🎯 Transcribing audio (this may take a while)...")
        progress_bar.progress(30)
        
        transcript = services['transcription'].transcribe(temp_path)
        progress_bar.progress(60)
        
        if not transcript or not transcript.strip():
            st.error("❌ No speech detected in the audio file. Please check the audio quality.")
            return
        
        # Step 4: AI Analysis
        status_text.text("🤖 Analyzing transcript with AI...")
        progress_bar.progress(70)
        
        analysis = st.session_state.ai_service.analyze_meeting(transcript)
        progress_bar.progress(90)
        
        # Step 5: Store meeting
        status_text.text("💾 Saving meeting data...")
        
        meeting_data = {
            'id': datetime.now().isoformat(),
            'title': title,
            'date': str(date),
            'notes': notes,
            'duration': audio_info['duration'],
            'file_size': audio_info['file_size'],
            'transcript': transcript,
            'analysis': analysis,
            'created_at': datetime.now().isoformat()
        }
        
        services['storage'].save_meeting(meeting_data)
        progress_bar.progress(100)
        status_text.text("✅ Meeting processed successfully!")
        
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)
        
        # Display results
        display_meeting_results(meeting_data)
        
        # Rerun to update sidebar stats
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error processing meeting: {str(e)}")
        if 'temp_path' in locals() and temp_path:
            try:
                os.unlink(temp_path)
            except Exception:
                pass

def display_meeting_results(meeting_data):
    st.success("🎉 Meeting analysis complete!")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Summary", "📝 Full Transcript", "✅ Action Items", "🏛️ Key Decisions"])
    
    with tab1:
        st.subheader("Meeting Summary")
        if meeting_data['analysis'].get('summary'):
            st.markdown(meeting_data['analysis']['summary'])
        else:
            st.info("No summary available")
    
    with tab2:
        st.subheader("Full Transcript")
        st.text_area("Transcript", meeting_data['transcript'], height=400, disabled=True)
        
        # Audio info
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Duration", f"{meeting_data['duration']:.1f} minutes")
        with col2:
            st.metric("File Size", f"{meeting_data['file_size']:.1f} MB")
    
    with tab3:
        st.subheader("Action Items")
        action_items = meeting_data['analysis'].get('action_items', [])
        if action_items:
            for i, item in enumerate(action_items, 1):
                st.markdown(f"{i}. {item}")
        else:
            st.info("No action items identified")
    
    with tab4:
        st.subheader("Key Decisions")
        decisions = meeting_data['analysis'].get('key_decisions', [])
        if decisions:
            for i, decision in enumerate(decisions, 1):
                st.markdown(f"{i}. {decision}")
        else:
            st.info("No key decisions identified")
    
    # Export options
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Export as Markdown"):
            markdown_content = services['export'].to_markdown(meeting_data)
            st.download_button(
                label="Download Markdown File",
                data=markdown_content,
                file_name=f"{meeting_data['title']}_{meeting_data['date']}.md",
                mime="text/markdown"
            )
    
    with col2:
        if st.button("📊 Export as JSON"):
            import json
            json_content = json.dumps(meeting_data, indent=2)
            st.download_button(
                label="Download JSON File",
                data=json_content,
                file_name=f"{meeting_data['title']}_{meeting_data['date']}.json",
                mime="application/json"
            )

def meeting_archive_tab():
    st.header("Meeting Archive")
    
    meetings = services['storage'].get_all_meetings()
    
    if not meetings:
        st.info("No meetings found. Upload your first meeting to get started!")
        return
    
    # Display meetings
    for meeting in reversed(meetings):  # Show newest first
        with st.expander(f"📅 {meeting['title']} - {meeting['date']}", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Duration", f"{meeting['duration']:.1f} min")
            with col2:
                st.metric("Date", meeting['date'])
            with col3:
                if st.button("🗑️ Delete", key=f"del_{meeting['id']}"):
                    services['storage'].delete_meeting(meeting['id'])
                    st.rerun()
            
            if meeting.get('notes'):
                st.markdown(f"**Notes:** {meeting['notes']}")
            
            # Quick view of analysis
            if meeting['analysis'].get('summary'):
                st.markdown("**Summary:**")
                st.markdown(meeting['analysis']['summary'][:200] + "..." if len(meeting['analysis']['summary']) > 200 else meeting['analysis']['summary'])
            
            # Export for individual meeting
            col1, col2 = st.columns(2)
            with col1:
                markdown_content = services['export'].to_markdown(meeting)
                st.download_button(
                    label="📄 Export Markdown",
                    data=markdown_content,
                    file_name=f"{meeting['title']}_{meeting['date']}.md",
                    mime="text/markdown",
                    key=f"md_{meeting['id']}"
                )
            
            with col2:
                if st.button("👁️ View Details", key=f"view_{meeting['id']}"):
                    st.session_state.current_meeting = meeting
                    st.rerun()
    
    # Bulk operations
    if len(meetings) > 1:
        st.markdown("---")
        st.subheader("Bulk Operations")
        if st.button("🗑️ Clear All Meetings", type="secondary"):
            if st.session_state.get('confirm_clear'):
                services['storage'].clear_all_meetings()
                st.session_state.confirm_clear = False
                st.success("All meetings cleared!")
                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.warning("Click again to confirm deletion of all meetings.")

def search_meetings_tab():
    st.header("Search Meetings")
    
    meetings = services['storage'].get_all_meetings()
    
    if not meetings:
        st.info("No meetings to search. Upload some meetings first!")
        return
    
    # Search input
    search_query = st.text_input("🔍 Search in transcripts and summaries", placeholder="Enter keywords...")
    
    if search_query:
        # Simple text search
        matching_meetings = []
        query_lower = search_query.lower()
        
        for meeting in meetings:
            # Search in transcript, summary, title, and notes
            searchable_text = " ".join([
                meeting.get('title', ''),
                meeting.get('transcript', ''),
                meeting.get('notes', ''),
                meeting['analysis'].get('summary', ''),
                " ".join(meeting['analysis'].get('action_items', [])),
                " ".join(meeting['analysis'].get('key_decisions', []))
            ]).lower()
            
            if query_lower in searchable_text:
                matching_meetings.append(meeting)
        
        if matching_meetings:
            st.success(f"Found {len(matching_meetings)} matching meeting(s)")
            
            for meeting in matching_meetings:
                with st.expander(f"📅 {meeting['title']} - {meeting['date']}", expanded=True):
                    # Highlight search terms in summary
                    summary = meeting['analysis'].get('summary', 'No summary available')
                    st.markdown("**Summary:**")
                    st.markdown(summary)
                    
                    # Show action items if they contain search terms
                    action_items = meeting['analysis'].get('action_items', [])
                    if action_items:
                        st.markdown("**Action Items:**")
                        for item in action_items:
                            st.markdown(f"• {item}")
                    
                    # Export button
                    markdown_content = services['export'].to_markdown(meeting)
                    st.download_button(
                        label="📄 Export Markdown",
                        data=markdown_content,
                        file_name=f"{meeting['title']}_{meeting['date']}.md",
                        mime="text/markdown",
                        key=f"search_md_{meeting['id']}"
                    )
        else:
            st.warning("No meetings found matching your search query.")

if __name__ == "__main__":
    main()
