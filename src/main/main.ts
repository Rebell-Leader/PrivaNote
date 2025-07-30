import { app, BrowserWindow, ipcMain } from 'electron';
import * as path from 'path';
import { AudioCaptureService, AudioLevels, AudioPermissionStatus } from './services/AudioCaptureService';

class PrivaNoteApp {
  private mainWindow: BrowserWindow | null = null;
  private audioService: AudioCaptureService;

  constructor() {
    this.audioService = new AudioCaptureService();
    this.setupAudioServiceListeners();
    this.initializeApp();
  }

  private initializeApp(): void {
    // Handle app ready event
    app.whenReady().then(() => {
      this.createMainWindow();
      this.setupIpcHandlers();

      app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
          this.createMainWindow();
        }
      });
    });

    // Handle window closed events
    app.on('window-all-closed', () => {
      if (process.platform !== 'darwin') {
        app.quit();
      }
    });
  }

  private createMainWindow(): void {
    this.mainWindow = new BrowserWindow({
      width: 1200,
      height: 800,
      minWidth: 800,
      minHeight: 600,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, 'preload.js'),
      },
      titleBarStyle: 'default',
      show: false, // Don't show until ready
    });

    // Load the renderer
    if (process.env.NODE_ENV === 'development') {
      this.mainWindow.loadURL('http://localhost:3000');
      this.mainWindow.webContents.openDevTools();
    } else {
      this.mainWindow.loadFile(path.join(__dirname, 'index.html'));
    }

    // Show window when ready
    this.mainWindow.once('ready-to-show', () => {
      this.mainWindow?.show();
    });

    // Handle window closed
    this.mainWindow.on('closed', () => {
      this.mainWindow = null;
    });
  }

  private setupAudioServiceListeners(): void {
    this.audioService.on('recordingStarted', (data) => {
      console.log('Recording started:', data);
      this.mainWindow?.webContents.send('audio:recordingStarted', data);
    });

    this.audioService.on('recordingStopped', (data) => {
      console.log('Recording stopped:', data);
      this.mainWindow?.webContents.send('audio:recordingStopped', data);
    });

    this.audioService.on('audioLevels', (levels: AudioLevels) => {
      this.mainWindow?.webContents.send('audio:audioLevels', levels);
    });
  }

  private setupIpcHandlers(): void {
    // App info handler
    ipcMain.handle('app:getVersion', () => {
      return app.getVersion();
    });

    // App control handlers
    ipcMain.handle('app:minimize', () => {
      this.mainWindow?.minimize();
    });

    ipcMain.handle('app:maximize', () => {
      if (this.mainWindow?.isMaximized()) {
        this.mainWindow.unmaximize();
      } else {
        this.mainWindow?.maximize();
      }
    });

    ipcMain.handle('app:close', () => {
      this.mainWindow?.close();
    });

    // Status update handler
    ipcMain.handle('app:updateStatus', (event, status: string) => {
      console.log('Status update:', status);
      return { success: true, status };
    });

    // Audio recording handlers
    ipcMain.handle('audio:startRecording', async (event, options) => {
      console.log('Start recording requested');
      return await this.audioService.startRecording(options);
    });

    ipcMain.handle('audio:stopRecording', async () => {
      console.log('Stop recording requested');
      return await this.audioService.stopRecording();
    });

    ipcMain.handle('audio:saveAudioData', async (event, audioBuffer: ArrayBuffer, mimeType?: string) => {
      console.log('Save audio data requested, size:', audioBuffer.byteLength, 'MIME type:', mimeType);
      const buffer = Buffer.from(audioBuffer);
      return await this.audioService.saveAudioData(buffer, mimeType);
    });

    ipcMain.handle('audio:checkPermissions', async () => {
      return await this.audioService.checkPermissions();
    });

    ipcMain.handle('audio:requestPermissions', async () => {
      return await this.audioService.requestPermissions();
    });

    ipcMain.handle('audio:getRecordingStatus', () => {
      return this.audioService.getRecordingStatus();
    });

    ipcMain.handle('audio:getAvailableDevices', async () => {
      return await this.audioService.getAvailableDevices();
    });

    // Forward audio levels from renderer to other listeners
    ipcMain.handle('audio:forwardAudioLevels', (event, levels) => {
      this.audioService.forwardAudioLevels(levels);
    });
  }
}

// Initialize the application
new PrivaNoteApp();
