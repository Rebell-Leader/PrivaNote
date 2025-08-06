# PrivaNote - Privacy-First AI Meeting Assistant

## Overview

PrivaNote is a privacy-focused meeting assistant application built with Streamlit that provides local audio transcription and intelligent analysis capabilities. The application processes meeting recordings entirely on the user's device, ensuring complete data privacy while offering comprehensive meeting analysis features including summaries, action item extraction, and searchable meeting archives.

The system is designed around a modular architecture with separate services for audio processing, transcription, AI analysis, storage, and export functionality. It leverages local AI models (Whisper for transcription and planned integration with Gemma 3n E4B for analysis) to maintain privacy while providing enterprise-grade meeting intelligence.

## User Preferences

Preferred communication style: Simple, everyday language.
Vision: Cross-platform, local AI meeting assistant using Gemma 3n E4B and Whisper for privacy-first intelligent transcription and analysis.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application with responsive layout
- **State Management**: Session-based storage using Streamlit's built-in session state
- **UI Components**: Wide layout with expandable sidebar and privacy-focused design
- **Caching**: Resource caching for service initialization to improve performance

### Backend Architecture
- **Modular Service Design**: Five core services handle distinct responsibilities:
  - AudioProcessor: Handles file format conversion and metadata extraction
  - TranscriptionService: Local audio-to-text conversion using faster-whisper
  - AIAnalysisService: Meeting content analysis (currently OpenAI API, planned Gemma integration)
  - StorageService: Local data persistence in browser session
  - ExportService: Multi-format export capabilities (Markdown, JSON planned)

### Audio Processing Pipeline
- **Input Support**: Multiple audio formats (WAV, MP3, MP4, M4A, FLAC, OGG)
- **Preprocessing**: Automatic conversion to WAV format for optimal Whisper compatibility
- **Metadata Extraction**: Duration, file size, sample rate, and channel information
- **Quality Optimization**: Format standardization for consistent transcription results

### Transcription Architecture
- **Local Processing**: faster-whisper implementation for on-device transcription
- **Model Management**: Configurable model sizes with automatic device detection
- **Performance Optimization**: CPU/GPU automatic selection with appropriate compute types
- **Language Support**: Automatic language detection with manual override capability

### AI Analysis System
- **Current Implementation**: OpenAI API integration (gpt-4o) for comprehensive meeting analysis
- **Future Plans**: Transition to local Gemma 3n E4B model for complete privacy
- **API Configuration**: Uses OPENAI_API_KEY environment variable
- **Analysis Capabilities**: 
  - Meeting summarization
  - Action item extraction
  - Key decision identification
  - Topic classification
  - Participant identification
  - Next steps generation
- **Fallback Mechanism**: Basic analysis when AI services unavailable

### Data Storage Strategy
- **Local-First**: All data stored in browser session state
- **Privacy by Design**: No external data transmission for core functionality
- **Session Persistence**: Meeting data maintained during browser session
- **Export Options**: Multiple format support for data portability

### Export System
- **Format Support**: Markdown export with structured meeting data
- **Data Preservation**: Complete meeting information including metadata
- **User Control**: Local file generation for meeting records

## External Dependencies

### AI Models and Services
- **faster-whisper**: Local speech-to-text transcription model
- **OpenAI API**: Current AI analysis service (optional, requires API key)
- **Gemma 3n E4B**: Planned local AI model for privacy-first analysis

### Audio Processing
- **pydub**: Audio file manipulation and format conversion
- **AudioSegment**: Audio metadata extraction and processing

### Web Framework
- **Streamlit**: Main web application framework
- **pandas**: Data manipulation for meeting records

### Development Tools
- **tempfile**: Temporary file handling for audio processing
- **json**: Data serialization for storage and export
- **datetime**: Timestamp management for meeting records

### System Requirements
- **Python Environment**: Python 3.11+ with Streamlit deployment
- **Audio Codecs**: Support for WAV, MP3, MP4, M4A, FLAC, OGG formats
- **Model Storage**: Local caching for Whisper models (auto-downloaded)
- **Browser Compatibility**: Modern browser for Streamlit interface
- **Optional**: Ollama for local AI processing
- **Optional**: OpenAI API key for cloud analysis

### Documentation Structure
- **README.md**: Comprehensive setup and usage guide with privacy modes
- **SETUP.md**: Detailed installation instructions for multiple methods (uv, pip, direct)
- **replit.md**: Technical architecture and project memory
- **Streamlit Config**: Optimized deployment settings in .streamlit/config.toml

## Recent Changes

**August 2025 - Documentation & Dual-Mode AI Complete**
- ✅ Created comprehensive README.md with correct Streamlit setup instructions
- ✅ Added SETUP.md with multiple installation methods (uv, pip, direct)
- ✅ Implemented dual-mode AI integration (OpenAI + Ollama/Gemma 3n E4B)
- ✅ Enhanced CPU/non-CUDA device support for Whisper with automatic fallbacks
- ✅ Added interactive provider selection UI in sidebar with status indicators
- ✅ Improved privacy options with complete local processing capability
- ✅ Fixed AI Configuration interface with clickable dropdown and help buttons
- ✅ Added comprehensive documentation for different deployment scenarios