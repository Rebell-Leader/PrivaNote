# PrivaNote 🔒
![Privacy-First AI Meeting Assistant](https://img.shields.io/badge/Privacy-First-brightgreen) ![AI Powered](https://img.shields.io/badge/AI-Powered-blue) ![Local Processing](https://img.shields.io/badge/Local-Processing-orange)

**Privacy-First AI Meeting Assistant** - Local transcription and intelligent analysis with dual-mode AI processing.

## 🌟 Features

- **🎙️ Local Audio Transcription**: Powered by faster-whisper, processes audio entirely on your device
- **🤖 Dual-Mode AI Analysis**: Choose between OpenAI (cloud) or local Gemma 3n models via Ollama
- **🔒 Complete Privacy Control**: Audio files never leave your device, choose your privacy level
- **📊 Smart Meeting Intelligence**: Automatic summaries, action items, key decisions, and topic extraction
- **📁 Meeting Archive**: Searchable history with export to Markdown, JSON, and other formats
- **🌐 Web-Based Interface**: Modern, responsive UI accessible from any browser
- **⚡ Cross-Platform**: Runs on Windows, macOS, and Linux with automatic device optimization

## 🛡️ Privacy Modes

| Mode | Description | Privacy Level | Audio Processing | AI Analysis |
|------|-------------|---------------|------------------|-------------|
| **🏠 Local Gemma** | Complete privacy | 🟢 Maximum | Local (Whisper) | Local (Ollama/Gemma) |
| **☁️ OpenAI Cloud** | High-quality analysis | 🟡 Moderate | Local (Whisper) | Cloud (OpenAI API) |
| **🔧 Basic Analysis** | Keyword-based | 🟢 Maximum | Local (Whisper) | Local (Keywords) |

> **🔒 Your audio files never leave your device regardless of the AI mode you choose.**

## 🚀 Quick Start

### Option 1: Run on Replit (Easiest)
1. **Fork this Replit** or run directly in the browser
2. **Add OpenAI API Key** (optional): Go to Secrets tab → Add `OPENAI_API_KEY`
3. **Click Run** - The app will start automatically on port 5000
4. **Upload audio** and start analyzing your meetings!

### Option 2: Local Installation (Maximum Privacy)

#### Prerequisites
- Python 3.11 or higher
- Git

#### Installation Steps

1. **Clone the repository**
   ```bash
   git clone [<your-repo-url>](https://github.com/Rebell-Leader/PrivaNote)
   cd privanote
   ```

2. **Install dependencies**
   
   **Using uv (recommended):**
   ```bash
   pip install uv
   uv sync
   ```

   **Using pip:**
   ```bash
   pip install streamlit>=1.48.0 faster-whisper>=1.2.0 openai>=1.99.1 ollama>=0.5.2 pandas>=2.3.1 pydub>=0.25.1 torch>=2.8.0 torchaudio>=2.8.0
   ```

3. **Run the application**
   ```bash
   streamlit run app.py --server.port 5000
   ```

4. **Open your browser** to `http://localhost:5000`

#### 🏠 For Maximum Privacy: Local Ollama Setup

To enable completely local AI processing with Gemma 3n models:

1. **Install Ollama**
   ```bash
   # Windows/Mac: Download from https://ollama.com
   # Linux:
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **Install Gemma 3 models**
   ```bash
   # Recommended 4B model (balanced performance/quality)
   ollama pull gemma3
   
   # Alternative options:
   ollama pull gemma3:1b     # Faster, smaller (1.7GB)
   ollama pull gemma3:27b    # Highest quality (requires 16GB+ RAM)
   ```

3. **Restart the app** - Ollama integration will be automatically detected

## 📋 Usage Guide

### Basic Workflow
1. **Upload Audio**: Support for WAV, MP3, MP4, M4A, FLAC, OGG formats
2. **Choose AI Provider**: Select your preferred privacy/quality balance
3. **Review Results**: Automatically generated summaries, action items, and insights
4. **Export & Archive**: Save to Markdown, search previous meetings

### AI Provider Selection
- **OpenAI (Cloud)**: Requires API key, highest quality analysis
- **Local Gemma**: Requires Ollama setup, complete privacy
- **Basic Analysis**: No setup required, keyword-based extraction

### Supported Audio Formats
- WAV, MP3, MP4, M4A, FLAC, OGG
- Automatic format conversion for optimal Whisper compatibility
- Works with virtual meeting recordings (Zoom, Teams, etc.)

## 🏗️ Technical Architecture

### Core Components
- **Frontend**: Streamlit web application with responsive design
- **Audio Processing**: PyDub for format conversion and metadata extraction
- **Transcription**: faster-whisper for local speech-to-text
- **AI Analysis**: Dual-mode system (OpenAI API + Ollama integration)
- **Storage**: Local browser session with export capabilities

### Technology Stack
- **Python 3.11+** - Core runtime
- **Streamlit** - Web framework and UI
- **faster-whisper** - Local speech recognition
- **OpenAI API** - Cloud AI analysis (optional)
- **Ollama + Gemma 3n** - Local AI analysis (optional)
- **PyTorch** - ML framework with CPU/GPU optimization

### Privacy by Design
- **Local-first processing**: Audio transcription happens on your device
- **Configurable AI providers**: Choose your privacy level
- **No persistent storage**: Data only in browser session
- **Export control**: You decide what data to keep

## 🎯 Use Cases

### 👔 For Business Professionals
- **Meetings**: Capture decisions, action items, and follow-ups
- **Interviews**: Generate structured candidate assessments
- **Client Calls**: Track requirements and commitments
- **Team Standups**: Document progress and blockers

### 🚀 For Founders & Entrepreneurs  
- **Investor Meetings**: Capture feedback and next steps
- **Team Updates**: Track project progress and decisions
- **Customer Discovery**: Organize insights and pain points
- **Board Meetings**: Generate structured reports and summaries

### 🏢 For Enterprise Teams
- **Compliance**: Maintain meeting records with privacy controls
- **Knowledge Management**: Build searchable meeting archives
- **Remote Work**: Enhance async communication with meeting summaries
- **Training**: Create documentation from recorded sessions

## 🔧 Configuration

### Environment Variables
```bash
# Optional: OpenAI API key for cloud analysis
OPENAI_API_KEY=your_openai_api_key

# Optional: Custom Ollama host (default: localhost:11434)
OLLAMA_HOST=localhost:11434
```

### Streamlit Configuration
The app includes optimized settings in `.streamlit/config.toml`:
- Headless mode for deployment
- Proper host binding (0.0.0.0:5000)
- Performance optimizations

## 🐛 Troubleshooting

### Common Issues

**Whisper initialization fails:**
- The app automatically tries multiple device configurations
- CPU mode with int8 compute type should work on any system
- Check error messages in the console for specific issues

**OpenAI API errors:**
- Verify your API key is correctly set in environment variables
- Ensure you have sufficient API credits
- Check your internet connection

**Ollama not detected:**
- Make sure Ollama service is running (`ollama serve`)
- Verify models are installed (`ollama list`)
- Check if port 11434 is accessible

**Audio upload issues:**
- Supported formats: WAV, MP3, MP4, M4A, FLAC, OGG
- Maximum file size depends on available memory
- Try converting audio to WAV format if issues persist

### Performance Tips
- **CPU-only systems**: Use Whisper's int8 mode (automatic)
- **GPU systems**: CUDA acceleration (automatic detection)
- **Large files**: Consider splitting into smaller segments
- **Memory usage**: Close unused browser tabs during processing

## 🤝 Contributing

We welcome contributions! Areas where you can help:

- **🐛 Bug fixes** - Report issues and submit fixes
- **🎨 UI/UX improvements** - Enhance the user interface
- **🔌 Integrations** - Add support for more AI models or export formats
- **📚 Documentation** - Improve setup guides and usage examples
- **🧪 Testing** - Test across different platforms and configurations

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🗺️ Roadmap

### 🎯 Near Term
- **Speaker diarization** - Identify individual speakers
- **Real-time processing** - Live meeting transcription
- **Mobile support** - Responsive design improvements
- **API integrations** - Notion, Confluence, Slack export

### 🚀 Future Vision
- **Native mobile apps** - iOS and Android with local AI
- **Team collaboration** - Shared meeting spaces
- **Advanced search** - Semantic search across meeting history
- **Custom models** - Fine-tuned models for specific domains
- **Workflow automation** - Trigger actions based on meeting content

## 💬 Support & Community

- **Issues**: [GitHub Issues](https://github.com/your-username/privanote/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/privanote/discussions)
- **Documentation**: This README and inline help
- **Email**: [Contact us](mailto:your-email@example.com)

## 🙏 Acknowledgments

- **OpenAI** - Whisper model and API services
- **Google** - Gemma 3n models and research
- **Ollama** - Local model serving platform  
- **Streamlit** - Web application framework
- **faster-whisper** - Optimized Whisper implementation

---

**Built with ❤️ for privacy-conscious professionals who want AI-powered meeting intelligence without compromising their data security.**