import React, { useState, useEffect, useRef } from 'react';
import {
  TitleBar,
  Header,
  ControlPanel,
  ProgressIndicator,
  ResultsSection,
  PermissionsDialog,
  AudioSourceSelector,
} from './components';
import { EnhancedAudioCapture } from './services/EnhancedAudioCapture';

interface AudioLevels {
  microphone: number;
  system: number;
  timestamp: number;
}

interface AudioPermissions {
  microphone: boolean;
  system: boolean;
  screen: boolean;
  error?: string;
}

const App: React.FC = () => {
  const [appVersion, setAppVersion] = useState<string>('1.0.0');
  const [status, setStatus] = useState<string>('Ready');
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [hasResults, setHasResults] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [progressMessage, setProgressMessage] = useState<string>('');
  const [audioLevels, setAudioLevels] = useState<AudioLevels>({ microphone: 0, system: 0, timestamp: 0 });
  const [showPermissionsDialog, setShowPermissionsDialog] = useState<boolean>(false);
  const [showAudioSourceSelector, setShowAudioSourceSelector] = useState<boolean>(false);
  const [permissions, setPermissions] = useState<AudioPermissions>({ microphone: false, system: false, screen: false });
  const [audioSources, setAudioSources] = useState<{ microphone: boolean; systemAudio: boolean; selectedMicId?: string }>({ microphone: true, systemAudio: true });

  const enhancedAudioCapture = useRef<EnhancedAudioCapture | null>(null);

  useEffect(() => {
    // Initialize EnhancedAudioCapture
    enhancedAudioCapture.current = new EnhancedAudioCapture();

    // Set up EnhancedAudioCapture callbacks
    enhancedAudioCapture.current.setOnAudioLevels((levels: AudioLevels) => {
      setAudioLevels(levels);
      // Forward levels to main process for other listeners
      window.electronAPI.forwardAudioLevels(levels);
    });

    enhancedAudioCapture.current.setOnDataAvailable(async (audioBlob: Blob) => {
      try {
        // Convert blob to ArrayBuffer and send to main process
        const arrayBuffer = await audioBlob.arrayBuffer();
        const result = await window.electronAPI.saveAudioData(arrayBuffer, audioBlob.type);

        if (result.success) {
          console.log('Audio saved successfully to:', result.filePath);
          setStatus(`Recording saved to: ${result.filePath}`);
        } else {
          console.error('Failed to save audio:', result.error);
          setStatus(`Failed to save recording: ${result.error}`);
        }
      } catch (error) {
        console.error('Failed to process audio data:', error);
        setStatus('Failed to process audio data');
      }
    });

    // Get app version on startup
    const getVersion = async () => {
      try {
        const version = await window.electronAPI.getVersion();
        setAppVersion(version);
      } catch (error) {
        console.error('Failed to get app version:', error);
        setAppVersion('1.0.0'); // Fallback version
      }
    };

    // Check permissions on startup
    const checkPermissions = async () => {
      try {
        if (enhancedAudioCapture.current) {
          const permissionStatus = await enhancedAudioCapture.current.checkPermissions();
          setPermissions(permissionStatus);
        }
      } catch (error) {
        console.error('Failed to check permissions:', error);
        setPermissions({ microphone: false, system: false, screen: false, error: 'Failed to check permissions' });
      }
    };

    // Set up audio event listeners from main process
    window.electronAPI.onRecordingStarted((data) => {
      console.log('Recording started event:', data);
      setStatus('Recording in progress');
    });

    window.electronAPI.onRecordingStopped((data) => {
      console.log('Recording stopped event:', data);
      setStatus('Processing recording...');
    });

    getVersion();
    checkPermissions();

    // Cleanup listeners on unmount
    return () => {
      window.electronAPI.removeAllListeners('audio:recordingStarted');
      window.electronAPI.removeAllListeners('audio:recordingStopped');
    };
  }, []);

  const handleStartRecording = async () => {
    try {
      if (!enhancedAudioCapture.current) {
        setStatus('Audio capture not initialized');
        return;
      }

      // Check permissions first
      const permissionStatus = await enhancedAudioCapture.current.checkPermissions();
      setPermissions(permissionStatus);

      // Show audio source selector if we have options
      if (permissionStatus.microphone || permissionStatus.system) {
        setShowAudioSourceSelector(true);
        return;
      }

      // If no permissions, show permissions dialog
      setShowPermissionsDialog(true);
    } catch (error) {
      console.error('Failed to start recording:', error);
      setStatus('Failed to start recording');
      setIsProcessing(false);
    }
  };

  const handleAudioSourcesSelected = async (sources: { microphone: boolean; systemAudio: boolean; selectedMicId?: string }) => {
    try {
      if (!enhancedAudioCapture.current) {
        setStatus('Audio capture not initialized');
        return;
      }

      setAudioSources(sources);
      setStatus('Starting recording...');
      setProgressMessage('Initializing audio capture...');
      setIsProcessing(true);

      // Start recording in renderer process
      const audioResult = await enhancedAudioCapture.current.startRecording({
        sampleRate: 44100,
        channels: 2,
        bitDepth: 16,
        captureMicrophone: sources.microphone,
        captureSystemAudio: sources.systemAudio
      });

      if (!audioResult.success) {
        setStatus(`Failed to start audio capture: ${audioResult.error || 'Unknown error'}`);
        setIsProcessing(false);
        return;
      }

      // Notify main process
      const mainResult = await window.electronAPI.startRecording({
        sampleRate: 44100,
        channels: 2,
        bitDepth: 16
      });

      if (mainResult.success) {
        setIsRecording(true);
        setStatus('Recording in progress');
        setIsProcessing(false);
        await window.electronAPI.updateStatus('Recording started');
      } else {
        // Stop audio capture if main process failed
        await enhancedAudioCapture.current.stopRecording();
        setStatus(`Failed to start recording: ${mainResult.error || 'Unknown error'}`);
        setIsProcessing(false);
      }
    } catch (error) {
      console.error('Failed to start recording:', error);
      setStatus('Failed to start recording');
      setIsProcessing(false);
    }
  };

  const handleStopRecording = async () => {
    try {
      if (!enhancedAudioCapture.current) {
        setStatus('Audio capture not initialized');
        return;
      }

      setStatus('Stopping recording...');
      setProgressMessage('Saving recording...');
      setIsProcessing(true);

      // Stop recording in renderer process first
      const audioResult = await enhancedAudioCapture.current.stopRecording();
      if (!audioResult.success) {
        setStatus(`Failed to stop audio capture: ${audioResult.error || 'Unknown error'}`);
        setIsProcessing(false);
        return;
      }

      // Notify main process
      const result = await window.electronAPI.stopRecording();
      if (result.success) {
        setIsRecording(false);
        setStatus('Processing recording...');
        setProgressMessage('Transcribing audio and generating insights...');

        // Reset audio levels when recording stops
        setAudioLevels({ microphone: 0, system: 0, timestamp: Date.now() });

        // Simulate processing progress (this will be replaced with real progress in future tasks)
        simulateProcessing();

        await window.electronAPI.updateStatus(`Recording stopped. Saved to: ${result.filePath}`);
      } else {
        setStatus(`Failed to stop recording: ${result.error || 'Unknown error'}`);
        setIsProcessing(false);
      }
    } catch (error) {
      console.error('Failed to stop recording:', error);
      setStatus('Failed to stop recording');
      setIsProcessing(false);
    }
  };

  const simulateProcessing = () => {
    let currentProgress = 0;
    const interval = setInterval(() => {
      currentProgress += 10;
      setProgress(currentProgress);

      if (currentProgress >= 100) {
        clearInterval(interval);
        setIsProcessing(false);
        setHasResults(true);
        setStatus('Processing complete');
        setProgress(0);
      }
    }, 500);
  };

  const handleMinimize = () => {
    window.electronAPI.minimize();
  };

  const handleMaximize = () => {
    window.electronAPI.maximize();
  };

  const handleClose = () => {
    window.electronAPI.close();
  };

  const handleRequestPermissions = async () => {
    try {
      if (!enhancedAudioCapture.current) {
        setStatus('Audio capture not initialized');
        return;
      }

      const permissionStatus = await enhancedAudioCapture.current.requestPermissions();
      setPermissions(permissionStatus);

      if (permissionStatus.microphone || permissionStatus.system) {
        setShowPermissionsDialog(false);
        setStatus('Permissions granted. Ready to record.');
      } else {
        setStatus('Some permissions are still missing. Please check your system settings.');
      }
    } catch (error) {
      console.error('Failed to request permissions:', error);
      setStatus('Failed to request permissions');
    }
  };

  const handleClosePermissionsDialog = () => {
    setShowPermissionsDialog(false);
  };

  const handleCloseAudioSourceSelector = () => {
    setShowAudioSourceSelector(false);
  };

  const getAvailableAudioSources = async () => {
    if (enhancedAudioCapture.current) {
      return await enhancedAudioCapture.current.getAvailableAudioSources();
    }
    return [];
  };

  return (
    <div className="app">
      <TitleBar
        onMinimize={handleMinimize}
        onMaximize={handleMaximize}
        onClose={handleClose}
      />

      <div className="main-content">
        <Header appVersion={appVersion} />

        <ControlPanel
          isRecording={isRecording}
          status={status}
          audioLevels={audioLevels}
          onStartRecording={handleStartRecording}
          onStopRecording={handleStopRecording}
        />

        <ProgressIndicator
          isVisible={isProcessing}
          progress={progress}
          message={progressMessage}
          type={progress > 0 ? 'determinate' : 'indeterminate'}
        />

        <ResultsSection
          hasResults={hasResults}
          isProcessing={isProcessing && !isRecording}
        />
      </div>

      <PermissionsDialog
        isVisible={showPermissionsDialog}
        permissions={permissions}
        onRequestPermissions={handleRequestPermissions}
        onClose={handleClosePermissionsDialog}
      />

      <AudioSourceSelector
        isVisible={showAudioSourceSelector}
        onSourcesSelected={handleAudioSourcesSelected}
        onClose={handleCloseAudioSourceSelector}
        getAvailableSources={getAvailableAudioSources}
      />
    </div>
  );
};

export default App;
