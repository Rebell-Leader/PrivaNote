import { app, BrowserWindow, ipcMain } from 'electron';
import * as path from 'path';

class PrivaNoteApp {
  private mainWindow: BrowserWindow | null = null;

  constructor() {
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

    // Placeholder for future audio/AI handlers
    ipcMain.handle('audio:startRecording', async () => {
      console.log('Start recording requested');
      return { success: true, message: 'Recording started' };
    });

    ipcMain.handle('audio:stopRecording', async () => {
      console.log('Stop recording requested');
      return { success: true, message: 'Recording stopped' };
    });
  }
}

// Initialize the application
new PrivaNoteApp();
