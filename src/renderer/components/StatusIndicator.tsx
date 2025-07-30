import React from 'react';

interface StatusIndicatorProps {
  isRecording: boolean;
  status: string;
}

const StatusIndicator: React.FC<StatusIndicatorProps> = ({ isRecording, status }) => {
  const getStatusClass = () => {
    if (isRecording) return 'recording';
    if (status.toLowerCase().includes('error') || status.toLowerCase().includes('failed')) return 'error';
    if (status.toLowerCase().includes('processing') || status.toLowerCase().includes('starting')) return 'processing';
    return 'idle';
  };

  return (
    <div className="status-indicator">
      <div className="status-visual">
        <span className={`status-dot ${getStatusClass()}`}></span>
        <div className="status-text-container">
          <span className="status-text">{status}</span>
          <span className="status-label">
            {isRecording ? 'Recording Active' : 'Ready'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default StatusIndicator;
