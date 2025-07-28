# Requirements Document

## Introduction

PrivaNote MVP is a cross-platform, privacy-focused AI meeting assistant that leverages local models (Gemma 3n e4b and Whisper.cpp) to provide intelligent transcription, summarization, and structured note-taking. This MVP focuses on core functionality for desktop platforms (Windows, macOS, Linux) using Electron, with all processing happening locally to ensure complete data privacy. The goal is to create a functional demonstration suitable for the Gemini Hackathon that showcases local AI capabilities.

## Requirements

### Requirement 1: Local Audio Recording

**User Story:** As a meeting participant, I want to record audio from my system and microphone simultaneously, so that I can capture both my voice and the meeting audio from virtual platforms.

#### Acceptance Criteria

1. WHEN the user clicks "Start Recording" THEN the system SHALL begin capturing audio from both system output and microphone input
2. WHEN audio recording is active THEN the system SHALL display a visual indicator showing recording status
3. WHEN the user clicks "Stop Recording" THEN the system SHALL stop audio capture and save the recording locally
4. IF the system lacks audio permissions THEN the system SHALL prompt the user to grant necessary permissions
5. WHEN recording is in progress THEN the system SHALL show real-time audio level indicators

### Requirement 2: Local Speech-to-Text Processing

**User Story:** As a privacy-conscious user, I want my audio to be transcribed locally using Whisper.cpp, so that my meeting content never leaves my device.

#### Acceptance Criteria

1. WHEN audio recording stops THEN the system SHALL automatically begin transcription using local Whisper.cpp
2. WHEN transcription is processing THEN the system SHALL display progress indicators to the user
3. WHEN transcription completes THEN the system SHALL display the full transcript in the application
4. IF transcription fails THEN the system SHALL display an error message and allow retry
5. WHEN transcription is complete THEN the system SHALL store the transcript locally on the device

### Requirement 3: AI-Powered Content Processing

**User Story:** As a busy professional, I want Gemma 3n e4b to automatically generate summaries, action items, and key decisions from my meeting transcript, so that I can quickly review important information.

#### Acceptance Criteria

1. WHEN transcription is complete THEN the system SHALL process the transcript using local Gemma 3n e4b
2. WHEN AI processing completes THEN the system SHALL generate a concise meeting summary
3. WHEN AI processing completes THEN the system SHALL extract and list action items from the transcript
4. WHEN AI processing completes THEN the system SHALL identify and list key decisions made during the meeting
5. IF AI processing fails THEN the system SHALL display an error message and allow manual retry

### Requirement 4: User Interface and Controls

**User Story:** As a user, I want a simple and intuitive interface to control recording and view results, so that I can focus on my meetings without technical distractions.

#### Acceptance Criteria

1. WHEN the application launches THEN the system SHALL display a clean interface with prominent record/stop buttons
2. WHEN processing is occurring THEN the system SHALL show clear progress indicators and status messages
3. WHEN results are ready THEN the system SHALL display transcript, summary, action items, and decisions in organized sections
4. WHEN the user interacts with the interface THEN the system SHALL provide immediate visual feedback
5. WHEN content is displayed THEN the system SHALL allow users to scroll through and review all generated content (and edit, if needed)

### Requirement 5: Markdown Export Functionality

**User Story:** As a knowledge worker, I want to export my meeting notes as Markdown files, so that I can integrate them with my existing documentation and knowledge management systems.

#### Acceptance Criteria

1. WHEN processing is complete THEN the system SHALL provide an "Export to Markdown" button
2. WHEN the user clicks export THEN the system SHALL generate a well-formatted Markdown file containing transcript, summary, action items, and decisions
3. WHEN export is triggered THEN the system SHALL allow the user to choose the save location and filename
4. WHEN the file is saved THEN the system SHALL display a confirmation message with the file location
5. WHEN the Markdown file is created THEN it SHALL include proper formatting with headers, lists, and sections

### Requirement 6: Local Data Storage and Privacy

**User Story:** As a privacy-conscious professional, I want all my meeting data to be stored locally on my device, so that I maintain complete control over my sensitive information.

#### Acceptance Criteria

1. WHEN any data is processed THEN the system SHALL store all recordings, transcripts, and generated content locally only
2. WHEN the application runs THEN the system SHALL never send any audio or text data to external servers
3. WHEN data is stored THEN the system SHALL organize files in a clear local directory structure
4. WHEN the user wants to delete data THEN the system SHALL provide options to remove recordings and associated files
5. IF the application is uninstalled THEN the system SHALL leave user data intact unless explicitly requested to remove it

### Requirement 7: Cross-Platform Desktop Support

**User Story:** As a user working across different operating systems, I want PrivaNote to work consistently on Windows, macOS, and Linux, so that I can use it regardless of my platform.

#### Acceptance Criteria

1. WHEN the application is built THEN the system SHALL create installers for Windows, macOS, and Linux
2. WHEN running on any supported platform THEN the system SHALL provide identical core functionality
3. WHEN audio capture is initiated THEN the system SHALL work with platform-specific audio systems
4. WHEN the application launches THEN the system SHALL adapt to platform-specific UI conventions where appropriate
5. WHEN models are loaded THEN the system SHALL work efficiently on all supported platforms

### Requirement 8: Model Management and Setup

**User Story:** As a first-time user, I want the application to guide me through setting up the required AI models, so that I can start using PrivaNote without technical complexity.

#### Acceptance Criteria

1. WHEN the application first launches THEN the system SHALL check for required models (Whisper.cpp and Gemma 3n e4b)
2. IF models are missing THEN the system SHALL provide clear instructions for model download and setup
3. WHEN models are being loaded THEN the system SHALL display progress indicators
4. WHEN models are ready THEN the system SHALL confirm successful setup to the user
5. IF model loading fails THEN the system SHALL provide troubleshooting guidance and retry options
