import { contextBridge, ipcRenderer } from 'electron';

// Audio-related interfaces
export interface AudioCaptureOptions {
  sampleRate?: number;
  channels?: number;
  bitDepth?: number;
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

export interface RecordingResult {
  success: boolean;
  recordingId?: string;
  filePath?: string;
  duration?: number;
  error?: string;
}

export interface RecordingStatus {
  isRecording: boolean;
  recordingId: string;
  duration: number;
}

export interface AudioDevices {
  microphones: MediaDeviceInfo[];
  speakers: MediaDeviceInfo[];
}

// Define the API interface
export interface ElectronAPI {
  // App control methods
  getVersion: () => Promise<string>;
  minimize: () => Promise<void>;
  maximize: () => Promise<void>;
  close: () => Promise<void>;
  updateStatus: (status: string) => Promise<{ success: boolean; status: string }>;

  // Audio recording methods
  startRecording: (options?: AudioCaptureOptions) => Promise<RecordingResult>;
  stopRecording: () => Promise<RecordingResult>;
  saveAudioData: (audioBuffer: ArrayBuffer, mimeType?: string) => Promise<{ success: boolean; filePath?: string; error?: string }>;
  checkPermissions: () => Promise<AudioPermissionStatus>;
  requestPermissions: () => Promise<AudioPermissionStatus>;
  getRecordingStatus: () => Promise<RecordingStatus>;
  getAvailableDevices: () => Promise<AudioDevices>;
  forwardAudioLevels: (levels: AudioLevels) => Promise<void>;

  // Audio event listeners
  onRecordingStarted: (callback: (data: any) => void) => void;
  onRecordingStopped: (callback: (data: any) => void) => void;
  onAudioLevels: (callback: (levels: AudioLevels) => void) => void;
  removeAllListeners: (channel: string) => void;
}

// Expose the API to the renderer process
const electronAPI: ElectronAPI = {
  getVersion: () => ipcRenderer.invoke('app:getVersion'),
  minimize: () => ipcRenderer.invoke('app:minimize'),
  maximize: () => ipcRenderer.invoke('app:maximize'),
  close: () => ipcRenderer.invoke('app:close'),
  updateStatus: (status: string) => ipcRenderer.invoke('app:updateStatus', status),

  // Audio recording methods
  startRecording: (options?: AudioCaptureOptions) => ipcRenderer.invoke('audio:startRecording', options),
  stopRecording: () => ipcRenderer.invoke('audio:stopRecording'),
  saveAudioData: (audioBuffer: ArrayBuffer, mimeType?: string) => ipcRenderer.invoke('audio:saveAudioData', audioBuffer, mimeType),
  checkPermissions: () => ipcRenderer.invoke('audio:checkPermissions'),
  requestPermissions: () => ipcRenderer.invoke('audio:requestPermissions'),
  getRecordingStatus: () => ipcRenderer.invoke('audio:getRecordingStatus'),
  getAvailableDevices: () => ipcRenderer.invoke('audio:getAvailableDevices'),
  forwardAudioLevels: (levels: AudioLevels) => ipcRenderer.invoke('audio:forwardAudioLevels', levels),

  // Audio event listeners
  onRecordingStarted: (callback: (data: any) => void) => {
    ipcRenderer.on('audio:recordingStarted', (event, data) => callback(data));
  },
  onRecordingStopped: (callback: (data: any) => void) => {
    ipcRenderer.on('audio:recordingStopped', (event, data) => callback(data));
  },
  onAudioLevels: (callback: (levels: AudioLevels) => void) => {
    ipcRenderer.on('audio:audioLevels', (event, levels) => callback(levels));
  },
  removeAllListeners: (channel: string) => {
    ipcRenderer.removeAllListeners(channel);
  },
};

// Expose the API through context bridge
contextBridge.exposeInMainWorld('electronAPI', electronAPI);

// Type declaration for global window object
declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}
