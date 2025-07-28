# Design Document

## Overview

PrivaNote MVP is designed as a cross-platform desktop application built with Electron, leveraging local AI models for complete privacy. The architecture prioritizes local processing, minimal resource usage, and a clean user experience suitable for demonstration at the Gemini Hackathon. The application integrates Whisper.cpp for speech-to-text and Gemma 3n e4b for intelligent content processing, ensuring all sensitive meeting data remains on the user's device.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Electron Main Process                    │
├─────────────────────────────────────────────────────────────┤
│  Audio Capture Manager  │  Model Manager  │  File Manager   │
│  - System Audio         │  - Whisper.cpp  │  - Local Storage │
│  - Microphone           │  - Gemma 3n e4b │  - Export Utils  │
└─────────────────────────────────────────────────────────────┘
                                │
                                │ IPC Communication
                                │
┌─────────────────────────────────────────────────────────────┐
│                  Electron Renderer Process                  │
├─────────────────────────────────────────────────────────────┤
│              React-based User Interface                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │   Record    │ │  Progress   │ │      Results View       │ │
│  │  Controls   │ │ Indicators  │ │  - Transcript           │ │
│  │             │ │             │ │  - Summary              │ │
│  └─────────────┘ └─────────────┘ │  - Action Items         │ │
│                                  │  - Key Decisions        │ │
│                                  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Framework:** Electron (for cross-platform desktop support)
- **Frontend:** React with modern JavaScript/TypeScript
- **Backend:** Node.js with native module integration
- **Speech-to-Text:** Whisper.cpp (local C++ implementation)
- **AI Processing:** Gemma 3n e4b (local inference)
- **Audio Capture:** Platform-specific native modules
- **Storage:** Local file system with JSON metadata
- **Export:** Markdown generation utilities

## Components and Interfaces

### 1. Audio Capture Manager

**Purpose:** Handles system and microphone audio recording across platforms

**Key Methods:**
- `startRecording(options)` - Initiates audio capture
- `stopRecording()` - Stops capture and returns audio buffer
- `getAudioLevels()` - Returns real-time audio level data
- `checkPermissions()` - Verifies audio access permissions

**Platform Considerations:**
- Windows: DirectSound/WASAPI integration
- macOS: Core Audio framework with privacy permissions
- Linux: ALSA/PulseAudio support

### 2. Speech-to-Text Service

**Purpose:** Manages Whisper.cpp integration for local transcription

**Key Methods:**
- `transcribeAudio(audioBuffer)` - Processes audio and returns transcript
- `loadModel(modelPath)` - Initializes Whisper model
- `getProgress()` - Returns transcription progress status

**Implementation:**
- Native C++ addon wrapping whisper.cpp
- Asynchronous processing with progress callbacks
- Memory-efficient streaming for large audio files

### 3. AI Processing Service

**Purpose:** Handles Gemma 3n e4b integration for content analysis

**Key Methods:**
- `generateSummary(transcript)` - Creates meeting summary
- `extractActionItems(transcript)` - Identifies action items
- `identifyDecisions(transcript)` - Extracts key decisions
- `loadModel()` - Initializes Gemma model

**Prompt Engineering:**
```
Summary Prompt: "Analyze this meeting transcript and provide a concise summary highlighting the main topics discussed, key points raised, and overall meeting outcome. Keep it under 200 words."

Action Items Prompt: "Extract all action items from this meeting transcript. Format as a numbered list with clear ownership and deadlines where mentioned."

Decisions Prompt: "Identify all key decisions made during this meeting. List each decision clearly with any relevant context or conditions."
```

### 4. File Management System

**Purpose:** Handles local storage, organization, and export functionality

**Directory Structure:**
```
~/PrivaNote/
├── recordings/
│   ├── 2024-01-15_meeting-001.wav
│   └── 2024-01-15_meeting-002.wav
├── transcripts/
│   ├── 2024-01-15_meeting-001.json
│   └── 2024-01-15_meeting-002.json
└── exports/
    ├── 2024-01-15_meeting-001.md
    └── 2024-01-15_meeting-002.md
```

**Key Methods:**
- `saveRecording(audioBuffer, metadata)` - Stores audio with metadata
- `saveTranscript(transcript, analysis)` - Stores processed results
- `exportToMarkdown(sessionId)` - Generates formatted export
- `listSessions()` - Returns available meeting sessions

### 5. User Interface Components

**Main Window Layout:**
- Header: Application title and status indicators
- Control Panel: Record/Stop buttons with audio level meters
- Progress Area: Processing status and progress bars
- Results Tabs: Transcript, Summary, Action Items, Decisions
- Export Section: Markdown export button and options

**State Management:**
- Recording state (idle, recording, processing, complete)
- Audio levels and permissions status
- Processing progress for STT and AI analysis
- Results data and export status

## Data Models

### Recording Session
```typescript
interface RecordingSession {
  id: string;
  timestamp: Date;
  duration: number;
  audioPath: string;
  status: 'recording' | 'processing' | 'complete' | 'error';
  metadata: {
    sampleRate: number;
    channels: number;
    format: string;
  };
}
```

### Transcript Data
```typescript
interface TranscriptData {
  sessionId: string;
  rawTranscript: string;
  confidence: number;
  processingTime: number;
  segments: Array<{
    start: number;
    end: number;
    text: string;
  }>;
}
```

### AI Analysis Results
```typescript
interface AnalysisResults {
  sessionId: string;
  summary: string;
  actionItems: Array<{
    item: string;
    owner?: string;
    deadline?: string;
  }>;
  keyDecisions: Array<{
    decision: string;
    context: string;
  }>;
  processingTime: number;
}
```

## Error Handling

### Audio Capture Errors
- Permission denied: Guide user through system settings
- Device not found: List available audio devices
- Recording failure: Provide retry mechanism with diagnostics

### Model Loading Errors
- Missing models: Provide download instructions and links
- Insufficient memory: Suggest closing other applications
- Corrupted models: Offer re-download option

### Processing Errors
- Transcription failure: Allow manual retry with different settings
- AI processing timeout: Implement fallback with basic text processing
- Export errors: Validate file permissions and disk space

## Testing Strategy

### Unit Testing
- Audio capture functionality across platforms
- Model loading and inference accuracy
- File operations and data persistence
- Export format validation

### Integration Testing
- End-to-end recording to export workflow
- Cross-platform compatibility testing
- Performance testing with various audio lengths
- Memory usage monitoring during processing

### User Acceptance Testing
- Recording quality in different environments
- UI responsiveness during processing
- Export file quality and formatting
- Installation and setup process

### Performance Benchmarks
- Target: < 30 seconds for 10-minute meeting transcription
- Target: < 60 seconds for AI processing of 10-minute transcript
- Target: < 500MB memory usage during peak processing
- Target: < 2GB disk space for complete installation

## Security and Privacy Considerations

### Data Protection
- All processing occurs locally with no network communication
- Audio files encrypted at rest using system-level encryption
- Temporary files securely deleted after processing
- No telemetry or usage data collection

### Model Security
- Verify model integrity using checksums
- Secure model download over HTTPS
- Local model storage with appropriate file permissions
- Regular security updates for dependencies

## Deployment and Distribution

### Build Process
- Electron Builder for cross-platform packaging
- Code signing for Windows and macOS
- Automated testing in CI/CD pipeline
- Dependency bundling for offline operation

### Installation Requirements
- Minimum 4GB RAM (8GB recommended)
- 2GB free disk space for models and application
- Modern CPU with AVX support for optimal performance
- Audio input/output devices and permissions
