import { EventEmitter } from 'events';
import * as fs from 'fs';
import * as path from 'path';

export interface AudioCaptureOptions {
  sampleRate: number;
  channels: number;
  bitDepth: number;
  deviceId?: string;
}

export interface AudioLevels {
  microphone: number;
  system: number;
  timestamp: number;
}

export interface AudioPermissionStatus {
  microphone: boolean;
  system: boolean;
  error?: string;
}

export class AudioCaptureService extends EventEmitter {
  private isRecording: boolean = false;
  private recordingStartTime: number = 0;
  private recordingId: string = '';
  private recordingsDir: string;
  private currentRecordingPath: string = '';

  constructor() {
    super();

    // Create recordings directory
    this.recordingsDir = path.join(process.cwd(), 'recordings');
    this.ensureDirectoryExists(this.recordingsDir);
  }

  private ensureDirectoryExists(dirPath: string): void {
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
    }
  }

  public async checkPermissions(): Promise<AudioPermissionStatus> {
    // Permissions will be checked in the renderer process
    // This is just a placeholder that returns optimistic results
    return {
      microphone: true,
      system: true,
    };
  }

  public async startRecording(options?: Partial<AudioCaptureOptions>): Promise<{ success: boolean; recordingId: string; error?: string }> {
    if (this.isRecording) {
      return { success: false, recordingId: '', error: 'Already recording' };
    }

    try {
      // Generate recording ID and file path (we'll update the extension when we know the MIME type)
      this.recordingId = `recording_${Date.now()}`;
      this.recordingStartTime = Date.now();
      this.currentRecordingPath = path.join(this.recordingsDir, `${this.recordingId}.webm`);
      this.isRecording = true;

      // Emit recording started event
      this.emit('recordingStarted', {
        recordingId: this.recordingId,
        options: options || { sampleRate: 44100, channels: 2, bitDepth: 16 },
        timestamp: this.recordingStartTime,
      });

      return { success: true, recordingId: this.recordingId };
    } catch (error) {
      return {
        success: false,
        recordingId: '',
        error: error instanceof Error ? error.message : 'Failed to start recording'
      };
    }
  }

  public async stopRecording(): Promise<{ success: boolean; filePath?: string; duration?: number; error?: string }> {
    if (!this.isRecording) {
      return { success: false, error: 'Not currently recording' };
    }

    try {
      this.isRecording = false;
      const duration = Date.now() - this.recordingStartTime;

      // The actual file saving will be handled by the renderer process
      // This just manages the state and emits events

      // Emit recording stopped event
      this.emit('recordingStopped', {
        recordingId: this.recordingId,
        filePath: this.currentRecordingPath,
        duration,
        timestamp: Date.now(),
      });

      return { success: true, filePath: this.currentRecordingPath, duration };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to stop recording'
      };
    }
  }

  public async saveAudioData(audioBlob: Buffer, mimeType?: string): Promise<{ success: boolean; filePath?: string; error?: string }> {
    try {
      if (!this.currentRecordingPath) {
        return { success: false, error: 'No active recording to save' };
      }

      // Update file extension based on MIME type if provided
      if (mimeType) {
        const extension = this.getFileExtensionFromMimeType(mimeType);
        const basePath = this.currentRecordingPath.replace(/\.[^/.]+$/, '');
        this.currentRecordingPath = `${basePath}.${extension}`;
      }

      console.log('Saving audio data to:', this.currentRecordingPath, 'Size:', audioBlob.length, 'bytes');

      // Save the audio data to file
      fs.writeFileSync(this.currentRecordingPath, audioBlob);

      // Verify the file was written correctly
      const stats = fs.statSync(this.currentRecordingPath);
      console.log('File saved successfully. Size on disk:', stats.size, 'bytes');

      return { success: true, filePath: this.currentRecordingPath };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to save audio data'
      };
    }
  }

  private getFileExtensionFromMimeType(mimeType: string): string {
    if (mimeType.includes('webm')) return 'webm';
    if (mimeType.includes('ogg')) return 'ogg';
    if (mimeType.includes('mp4')) return 'mp4';
    if (mimeType.includes('wav')) return 'wav';
    return 'webm'; // fallback
  }

  public forwardAudioLevels(levels: AudioLevels): void {
    if (this.isRecording) {
      this.emit('audioLevels', levels);
    }
  }

  public getRecordingStatus(): { isRecording: boolean; recordingId: string; duration: number } {
    return {
      isRecording: this.isRecording,
      recordingId: this.recordingId,
      duration: this.isRecording ? Date.now() - this.recordingStartTime : 0,
    };
  }

  public getAvailableDevices(): Promise<{ microphones: MediaDeviceInfo[]; speakers: MediaDeviceInfo[] }> {
    // Device enumeration will be handled in the renderer process
    return Promise.resolve({
      microphones: [
        { deviceId: 'default', label: 'Default Microphone', kind: 'audioinput' } as MediaDeviceInfo,
      ],
      speakers: [
        { deviceId: 'default', label: 'Default Speaker', kind: 'audiooutput' } as MediaDeviceInfo,
      ],
    });
  }

  public async requestPermissions(): Promise<AudioPermissionStatus> {
    // Permission requests will be handled in the renderer process
    return this.checkPermissions();
  }
}
