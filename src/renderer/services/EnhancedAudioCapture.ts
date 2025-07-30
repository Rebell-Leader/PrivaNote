export interface AudioCaptureOptions {
  sampleRate: number;
  channels: number;
  bitDepth: number;
  captureSystemAudio: boolean;
  captureMicrophone: boolean;
}

export interface AudioLevels {
  microphone: number;
  system: number;
  timestamp: number;
}

export interface AudioSource {
  id: string;
  label: string;
  type: 'microphone' | 'system' | 'screen';
  deviceId?: string;
}

export class EnhancedAudioCapture {
  private audioContext: AudioContext | null = null;
  private microphoneStream: MediaStream | null = null;
  private systemStream: MediaStream | null = null;
  private combinedStream: MediaStream | null = null;
  private mediaRecorder: MediaRecorder | null = null;
  private micAnalyser: AnalyserNode | null = null;
  private systemAnalyser: AnalyserNode | null = null;
  private audioChunks: Blob[] = [];
  private isRecording: boolean = false;
  private levelMonitoringInterval: number | null = null;
  private onAudioLevels: ((levels: AudioLevels) => void) | null = null;
  private onDataAvailable: ((audioBlob: Blob) => void) | null = null;

  constructor() {}

  public async checkPermissions(): Promise<{ microphone: boolean; system: boolean; screen: boolean; error?: string }> {
    try {
      const permissions = {
        microphone: false,
        system: false,
        screen: false,
        error: undefined as string | undefined
      };

      // Check microphone permission
      try {
        const micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        micStream.getTracks().forEach(track => track.stop());
        permissions.microphone = true;
      } catch (error) {
        console.warn('Microphone permission denied:', error);
      }

      // Check screen capture permission (which can include system audio)
      try {
        if ('getDisplayMedia' in navigator.mediaDevices) {
          const screenStream = await navigator.mediaDevices.getDisplayMedia({
            video: true,
            audio: true
          });
          screenStream.getTracks().forEach(track => track.stop());
          permissions.screen = true;
          permissions.system = true; // Screen capture can include system audio
        }
      } catch (error) {
        console.warn('Screen capture permission denied:', error);
      }

      return permissions;
    } catch (error) {
      return {
        microphone: false,
        system: false,
        screen: false,
        error: error instanceof Error ? error.message : 'Unknown error checking permissions'
      };
    }
  }

  public async getAvailableAudioSources(): Promise<AudioSource[]> {
    const sources: AudioSource[] = [];

    try {
      // Get audio input devices
      const devices = await navigator.mediaDevices.enumerateDevices();

      devices.forEach(device => {
        if (device.kind === 'audioinput') {
          sources.push({
            id: device.deviceId,
            label: device.label || `Microphone ${device.deviceId.slice(0, 8)}`,
            type: 'microphone',
            deviceId: device.deviceId
          });
        }
      });

      // Add system audio option (via screen capture)
      if ('getDisplayMedia' in navigator.mediaDevices) {
        sources.push({
          id: 'system-audio',
          label: 'System Audio (via Screen Capture)',
          type: 'system'
        });
      }

      // Add screen capture option
      if ('getDisplayMedia' in navigator.mediaDevices) {
        sources.push({
          id: 'screen-capture',
          label: 'Screen with Audio',
          type: 'screen'
        });
      }

    } catch (error) {
      console.error('Failed to enumerate audio sources:', error);
    }

    return sources;
  }

  public async startRecording(options: AudioCaptureOptions): Promise<{ success: boolean; error?: string }> {
    if (this.isRecording) {
      return { success: false, error: 'Already recording' };
    }

    try {
      console.log('Starting enhanced audio capture with options:', options);

      // Create audio context
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({
        sampleRate: options.sampleRate
      });

      const audioTracks: MediaStreamTrack[] = [];

      // Capture microphone if requested
      if (options.captureMicrophone) {
        try {
          this.microphoneStream = await navigator.mediaDevices.getUserMedia({
            audio: {
              echoCancellation: false,
              noiseSuppression: false,
              autoGainControl: false,
              sampleRate: options.sampleRate,
              channelCount: options.channels,
            }
          });

          console.log('Microphone stream acquired');
          audioTracks.push(...this.microphoneStream.getAudioTracks());

          // Set up microphone analysis
          this.setupMicrophoneAnalysis();
        } catch (error) {
          console.warn('Failed to capture microphone:', error);
        }
      }

      // Capture system audio if requested
      if (options.captureSystemAudio) {
        try {
          // Use screen capture to get system audio
          this.systemStream = await navigator.mediaDevices.getDisplayMedia({
            video: {
              width: { ideal: 1 },
              height: { ideal: 1 },
              frameRate: { ideal: 1 }
            },
            audio: {
              echoCancellation: false,
              noiseSuppression: false,
              autoGainControl: false,
              sampleRate: options.sampleRate,
            }
          });

          console.log('System audio stream acquired via screen capture');

          // Only add audio tracks, ignore video
          const systemAudioTracks = this.systemStream.getAudioTracks();
          audioTracks.push(...systemAudioTracks);

          // Set up system audio analysis
          this.setupSystemAudioAnalysis();
        } catch (error) {
          console.warn('Failed to capture system audio:', error);
        }
      }

      if (audioTracks.length === 0) {
        return { success: false, error: 'No audio sources available' };
      }

      // Create combined stream
      this.combinedStream = new MediaStream(audioTracks);

      // Create media recorder
      const mimeType = this.getSupportedMimeType();
      const mediaRecorderOptions: MediaRecorderOptions = { mimeType };

      console.log('Creating MediaRecorder with MIME type:', mimeType);
      this.mediaRecorder = new MediaRecorder(this.combinedStream, mediaRecorderOptions);

      // Set up recording event handlers
      this.setupRecordingHandlers(mimeType);

      // Start recording
      this.mediaRecorder.start(250);
      this.isRecording = true;

      // Start level monitoring
      this.startLevelMonitoring();

      console.log('Enhanced audio recording started');
      return { success: true };

    } catch (error) {
      this.cleanup();
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to start recording'
      };
    }
  }

  private setupMicrophoneAnalysis(): void {
    if (!this.audioContext || !this.microphoneStream) return;

    this.micAnalyser = this.audioContext.createAnalyser();
    this.micAnalyser.fftSize = 256;
    this.micAnalyser.smoothingTimeConstant = 0.8;

    const micSource = this.audioContext.createMediaStreamSource(this.microphoneStream);
    micSource.connect(this.micAnalyser);
  }

  private setupSystemAudioAnalysis(): void {
    if (!this.audioContext || !this.systemStream) return;

    const audioTracks = this.systemStream.getAudioTracks();
    if (audioTracks.length === 0) return;

    this.systemAnalyser = this.audioContext.createAnalyser();
    this.systemAnalyser.fftSize = 256;
    this.systemAnalyser.smoothingTimeConstant = 0.8;

    // Create a stream with only audio tracks for analysis
    const audioOnlyStream = new MediaStream(audioTracks);
    const systemSource = this.audioContext.createMediaStreamSource(audioOnlyStream);
    systemSource.connect(this.systemAnalyser);
  }

  private setupRecordingHandlers(mimeType: string): void {
    if (!this.mediaRecorder) return;

    this.audioChunks = [];

    this.mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        console.log('Audio chunk received:', event.data.size, 'bytes');
        this.audioChunks.push(event.data);
      }
    };

    this.mediaRecorder.onstop = () => {
      console.log('MediaRecorder stopped, total chunks:', this.audioChunks.length);
      const totalSize = this.audioChunks.reduce((sum, chunk) => sum + chunk.size, 0);
      console.log('Total audio data size:', totalSize, 'bytes');

      if (this.audioChunks.length === 0) {
        console.error('No audio chunks recorded!');
        return;
      }

      const audioBlob = new Blob(this.audioChunks, { type: mimeType });
      console.log('Created audio blob:', audioBlob.size, 'bytes, type:', audioBlob.type);

      if (this.onDataAvailable) {
        this.onDataAvailable(audioBlob);
      }
    };

    this.mediaRecorder.onerror = (event) => {
      console.error('MediaRecorder error:', event);
    };

    this.mediaRecorder.onstart = () => {
      console.log('MediaRecorder started');
    };
  }

  private startLevelMonitoring(): void {
    const updateLevels = () => {
      if (!this.isRecording) return;

      let micLevel = 0;
      let systemLevel = 0;

      // Get microphone level
      if (this.micAnalyser) {
        const bufferLength = this.micAnalyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        this.micAnalyser.getByteFrequencyData(dataArray);

        let sum = 0;
        for (let i = 0; i < bufferLength; i++) {
          sum += dataArray[i] * dataArray[i];
        }
        const rms = Math.sqrt(sum / bufferLength);
        micLevel = Math.min(100, Math.max(0, (rms / 255) * 100));
      }

      // Get system audio level
      if (this.systemAnalyser) {
        const bufferLength = this.systemAnalyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        this.systemAnalyser.getByteFrequencyData(dataArray);

        let sum = 0;
        for (let i = 0; i < bufferLength; i++) {
          sum += dataArray[i] * dataArray[i];
        }
        const rms = Math.sqrt(sum / bufferLength);
        systemLevel = Math.min(100, Math.max(0, (rms / 255) * 100));
      }

      const levels: AudioLevels = {
        microphone: micLevel,
        system: systemLevel,
        timestamp: Date.now()
      };

      if (this.onAudioLevels) {
        this.onAudioLevels(levels);
      }
    };

    this.levelMonitoringInterval = window.setInterval(updateLevels, 100);
  }

  public async stopRecording(): Promise<{ success: boolean; error?: string }> {
    if (!this.isRecording || !this.mediaRecorder) {
      return { success: false, error: 'Not currently recording' };
    }

    try {
      this.isRecording = false;

      // Stop level monitoring
      this.stopLevelMonitoring();

      // Create a promise to wait for the MediaRecorder to stop
      const stopPromise = new Promise<void>((resolve) => {
        if (this.mediaRecorder) {
          this.mediaRecorder.addEventListener('stop', () => resolve(), { once: true });
        } else {
          resolve();
        }
      });

      // Stop media recorder
      if (this.mediaRecorder.state === 'recording') {
        this.mediaRecorder.requestData();
        await new Promise(resolve => setTimeout(resolve, 100));
        this.mediaRecorder.stop();
        await stopPromise;
      }

      // Stop all streams
      this.stopAllStreams();

      // Close audio context
      if (this.audioContext && this.audioContext.state !== 'closed') {
        await this.audioContext.close();
      }

      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to stop recording'
      };
    } finally {
      this.cleanup();
    }
  }

  private stopAllStreams(): void {
    if (this.microphoneStream) {
      this.microphoneStream.getTracks().forEach(track => track.stop());
    }
    if (this.systemStream) {
      this.systemStream.getTracks().forEach(track => track.stop());
    }
    if (this.combinedStream) {
      this.combinedStream.getTracks().forEach(track => track.stop());
    }
  }

  private stopLevelMonitoring(): void {
    if (this.levelMonitoringInterval) {
      clearInterval(this.levelMonitoringInterval);
      this.levelMonitoringInterval = null;
    }
  }

  private getSupportedMimeType(): string {
    const types = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/ogg;codecs=opus',
      'audio/mp4',
      'audio/wav'
    ];

    for (const type of types) {
      if (MediaRecorder.isTypeSupported(type)) {
        console.log('Using MIME type:', type);
        return type;
      }
    }

    console.log('Using fallback MIME type: audio/webm');
    return 'audio/webm';
  }

  private cleanup(): void {
    this.stopLevelMonitoring();
    this.stopAllStreams();

    this.mediaRecorder = null;
    this.micAnalyser = null;
    this.systemAnalyser = null;
    this.audioContext = null;
    this.microphoneStream = null;
    this.systemStream = null;
    this.combinedStream = null;
    this.audioChunks = [];
  }

  public setOnAudioLevels(callback: (levels: AudioLevels) => void): void {
    this.onAudioLevels = callback;
  }

  public setOnDataAvailable(callback: (audioBlob: Blob) => void): void {
    this.onDataAvailable = callback;
  }

  public getRecordingStatus(): { isRecording: boolean } {
    return { isRecording: this.isRecording };
  }

  public async requestPermissions(): Promise<{ microphone: boolean; system: boolean; screen: boolean; error?: string }> {
    return this.checkPermissions();
  }
}
