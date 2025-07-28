import React, { useState, useEffect } from 'react';

const App: React.FC = () => {
  const [appVersion, setAppVersion] = useState<string>('');
  const [status, setStatus] = useState<string>('Ready');
  const [isRecording, setIsRecording] = useState<boolean>(false);

  useEffect(() => {
    // Get app version on startup
    const getVersion = async () => {
      try {
        const version = await window.electronAPI.getVersion();
        setAppVersion(version);
      } catch (error) {
        console.error('Failed to get app version:', error);
      }
    };

    getVersion();
  }, []);

  const handleStartRecording = async () => {
    try {
      setStatus('Starting recording...');
      const result = await window.electronAPI.startRecording();
      if (result.success) {
        setIsRecording(true);
        setStatus('Recording in progress');
        await window.electronAPI.updateStatus('Recording started');
      }
    } catch (error) {
      console.error('Failed to start recording:', error);
      setStatus('Failed to start recording');
    }
  };

  const handleStopRecording = async () => {
    try {
      setStatus('Stopping recording...');
      const result = await window.electronAPI.stopRecording();
      if (result.success) {
        setIsRecording(false);
        setStatus('Recording stopped');
        await window.electronAPI.updateStatus('Recording stopped');
      }
    } catch (error) {
      console.error('Failed to stop recording:', error);
      setStatus('Failed to stop recording');
    }
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
      {/* Title Bar */}
      <div className="title-bar">
        <div className="title-bar-left">
          <h1>PrivaNote</h1>
          <span className="version">v{appVersion}</span>
        </div>
        <div className="title-bar-right">
          <button className="title-button" onClick={handleMinimize}>−</button>
          <button className="title-button" onClick={handleMaximize}>□</button>
          <button className="title-button close" onClick={handleClose}>×</button>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Header */}
        <header className="header">
          <h2>AI Meeting Assistant</h2>
          <p>Privacy-focused local transcription and analysis</p>
        </header>

        {/* Control Panel */}
        <div className="control-panel">
          <div className="status-section">
            <div className="status-indicator">
              <span className={`status-dot ${isRecording ? 'recording' : 'idle'}`}></span>
              <span className="status-text">{status}</span>
            </div>
          </div>

          <div className="recording-controls">
            {!isRecording ? (
              <button
                className="record-button start"
                onClick={handleStartRecording}
              >
                <span className="button-icon">●</span>
                Start Recording
              </button>
            ) : (
              <button
                className="record-button stop"
                onClick={handleStopRecording}
              >
                <span className="button-icon">■</span>
                Stop Recording
              </button>
            )}
          </div>
        </div>

        {/* Results Area (Placeholder) */}
        <div className="results-area">
          <div className="results-placeholder">
            <h3>Results will appear here</h3>
            <p>Start a recording to see transcription and AI analysis</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
