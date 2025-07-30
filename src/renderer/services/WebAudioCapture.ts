export interface AudioCaptureOptions {
  sampleRate: number;
  channels: number;
  bitDepth: number;
}

export interface AudioLevels {
  microphone: number;
  system: number;
  timestamp: number;
}

export class WebAudioCapture {
  private audioContext: AudioContext | null = null;
  private mediaStream: MediaStream | null = null;
  private mediaRecorder: MediaRecorder | null = null;
  private analyserNode: AnalyserNode | null = null;
  private audioChunks: Blob[] = [];
  private isRecording: boolean = false;
  private levelMonitoringInterval: number | null = null;
  private onAudioLevels: ((levels: AudioLevels) => void) | null = null;
  private onDataAvailable: ((audioBlob: Blob) => void) | null = null;

  constructor() {}

  public async checkPermissions(): Promise<{ microphone: boolean; system: boolean; error?: string }> {
    try {
      // Check if getUserMedia is available
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        return {
          microphone: false,
          system: false,
          error: 'getUserMedia not supported in this browser'
        };
      }

      // Try to get microphone permission
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        stream.getTracks().forEach(track => track.stop()); // Stop immediately after checking

        return {
          microphone: true,
          system: true, // We'll capture system audio through the microphone for now
        };
      } catch (error) {
        return {
          microphone: false,
          system: false,
          error: error instanceof Error ? error.message : 'Permission denied'
        };
      }
    } catch (error) {
      return {
        microphone: false,
        system: false,
        error: error instanceof Error ? error.message : 'Unknown error checking permissions'
      };
    }
  }

  public async requestPermissions(): Promise<{ microphone: boolean; system: boolean; error?: string }> {
    return this.checkPermissions();
  }

  public async startRecording(options: AudioCaptureOptions = { sampleRate: 44100, channels: 2, bitDepth: 16 }): Promise<{ success: boolean; error?: string }> {
    if (this.isRecording) {
      return { success: false, error: 'Already recording' };
    }

    try {
      // Create audio context
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({
        sampleRate: options.sampleRate
      });

      // Get user media with high quality audio
      const constraints: MediaStreamConstraints = {
        audio: {
          echoCancellation: false,
          noiseSuppression: false,
          autoGainControl: false,
          sampleRate: options.sampleRate,
          channelCount: options.channels,
        }
      };

      console.log('Requesting media with constraints:', constraints);

      this.mediaStream = await navigator.mediaDevices.getUserMedia(constraints);

      // Create media recorder
      const mimeType = this.getSupportedMimeType();
      const mediaRecorderOptions: MediaRecorderOptions = {
        mimeType
      };

      // Only set audioBitsPerSecond if it's a reasonable value
      const bitRate = options.sampleRate * options.channels * (options.bitDepth / 8) * 8;
      if (bitRate >= 8000 && bitRate <= 320000) {
        mediaRecorderOptions.audioBitsPerSecond = bitRate;
      }

      console.log('MediaRecorder options:', mediaRecorderOptions);
      this.mediaRecorder = new MediaRecorder(this.mediaStream, mediaRecorderOptions);

      // Set up audio analysis for level monitoring
      this.setupAudioAnalysis();

      // Set up recording event handlers
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

      // Start recording
      this.mediaRecorder.start(250); // Collect data every 250ms for better responsiveness
      this.isRecording = true;

      // Start level monitoring
      this.startLevelMonitoring();

      return { success: true };
    } catch (error) {
      this.cleanup();
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to start recording'
      };
    }
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
        // Request any remaining data
        this.mediaRecorder.requestData();

        // Small delay to ensure data is collected
        await new Promise(resolve => setTimeout(resolve, 100));

        this.mediaRecorder.stop();
        // Wait for the stop event to ensure all data is processed
        await stopPromise;
      }

      // Stop all tracks
      if (this.mediaStream) {
        this.mediaStream.getTracks().forEach(track => track.stop());
      }

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
    return 'audio/webm'; // Fallback
  }

  private setupAudioAnalysis(): void {
    if (!this.audioContext || !this.mediaStream) return;

    // Create analyser node for level monitoring
    this.analyserNode = this.audioContext.createAnalyser();
    this.analyserNode.fftSize = 256;
    this.analyserNode.smoothingTimeConstant = 0.8;

    // Connect media stream to analyser
    const source = this.audioContext.createMediaStreamSource(this.mediaStream);
    source.connect(this.analyserNode);
  }

  private startLevelMonitoring(): void {
    if (!this.analyserNode) return;

    const bufferLength = this.analyserNode.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const updateLevels = () => {
      if (!this.isRecording || !this.analyserNode) return;

      this.analyserNode.getByteFrequencyData(dataArray);

      // Calculate RMS level
      let sum = 0;
      for (let i = 0; i < bufferLength; i++) {
        sum += dataArray[i] * dataArray[i];
      }
      const rms = Math.sqrt(sum / bufferLength);
      const level = (rms / 255) * 100; // Convert to 0-100 scale

      const levels: AudioLevels = {
        microphone: Math.min(100, Math.max(0, level)),
        system: Math.min(100, Math.max(0, level * 0.8)), // Simulate system audio as slightly lower
        timestamp: Date.now()
      };

      if (this.onAudioLevels) {
        this.onAudioLevels(levels);
      }
    };

    this.levelMonitoringInterval = window.setInterval(updateLevels, 100);
  }

  private stopLevelMonitoring(): void {
    if (this.levelMonitoringInterval) {
      clearInterval(this.levelMonitoringInterval);
      this.levelMonitoringInterval = null;
    }
  }

  private cleanup(): void {
    this.stopLevelMonitoring();

    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop());
      this.mediaStream = null;
    }

    this.mediaRecorder = null;
    this.analyserNode = null;
    this.audioContext = null;
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

  public async getAvailableDevices(): Promise<{ microphones: MediaDeviceInfo[]; speakers: MediaDeviceInfo[] }> {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();

      return {
        microphones: devices.filter(device => device.kind === 'audioinput'),
        speakers: devices.filter(device => device.kind === 'audiooutput')
      };
    } catch (error) {
      console.error('Failed to enumerate devices:', error);
      return { microphones: [], speakers: [] };
    }
  }
}
