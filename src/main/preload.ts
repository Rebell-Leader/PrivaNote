import { contextBridge, ipcRenderer } from 'electron';

// Define the API interface
export interface ElectronAPI {
  // App control methods
  getVersion: () => Promise<string>;
  minimize: () => Promise<void>;
  maximize: () => Promise<void>;
  close: () => Promise<void>;
  updateStatus: (status: string) => Promise<{ success: boolean; status: string }>;

  // Audio recording methods (placeholders for future implementation)
  startRecording: () => Promise<{ success: boolean; message: string }>;
  stopRecording: () => Promise<{ success: boolean; message: string }>;
}

// Expose the API to the renderer process
const electronAPI: ElectronAPI = {
  getVersion: () => ipcRenderer.invoke('app:getVersion'),
  minimize: () => ipcRenderer.invoke('app:minimize'),
  maximize: () => ipcRenderer.invoke('app:maximize'),
  close: () => ipcRenderer.invoke('app:close'),
  updateStatus: (status: string) => ipcRenderer.invoke('app:updateStatus', status),
  startRecording: () => ipcRenderer.invoke('audio:startRecording'),
  stopRecording: () => ipcRenderer.invoke('audio:stopRecording'),
};

// Expose the API through context bridge
contextBridge.exposeInMainWorld('electronAPI', electronAPI);

// Type declaration for global window object
declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}
