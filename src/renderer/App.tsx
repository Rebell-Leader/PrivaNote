import React, { useState, useEffect } from 'react';
import {
  TitleBar,
  Header,
  ControlPanel,
  ProgressIndicator,
  ResultsSection,
} from './components';

const App: React.FC = () => {
  const [appVersion, setAppVersion] = useState<string>('1.0.0');
  const [status, setStatus] = useState<string>('Ready');
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [hasResults, setHasResults] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [progressMessage, setProgressMessage] = useState<string>('');

  useEffect(() => {
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

    getVersion();
  }, []);

  const handleStartRecording = async () => {
    try {
      setStatus('Starting recording...');
      setProgressMessage('Initializing audio capture...');
      setIsProcessing(true);

      const result = await window.electronAPI.startRecording();
      if (result.success) {
        setIsRecording(true);
        setStatus('Recording in progress');
        setIsProcessing(false);
        await window.electronAPI.updateStatus('Recording started');
      } else {
        setStatus('Failed to start recording');
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
      setStatus('Stopping recording...');
      setProgressMessage('Saving recording...');
      setIsProcessing(true);

      const result = await window.electronAPI.stopRecording();
      if (result.success) {
        setIsRecording(false);
        setStatus('Processing recording...');
        setProgressMessage('Transcribing audio and generating insights...');

        // Simulate processing progress (this will be replaced with real progress in future tasks)
        simulateProcessing();

        await window.electronAPI.updateStatus('Recording stopped');
      } else {
        setStatus('Failed to stop recording');
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
    </div>
  );
};

export default App;
