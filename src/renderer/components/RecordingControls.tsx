import React from 'react';

interface RecordingControlsProps {
  isRecording: boolean;
  onStartRecording: () => void;
  onStopRecording: () => void;
}

const RecordingControls: React.FC<RecordingControlsProps> = ({
  isRecording,
  onStartRecording,
  onStopRecording,
}) => {
  return (
    <div className="recording-controls">
      {!isRecording ? (
        <button
          className="record-button start"
          onClick={onStartRecording}
          aria-label="Start recording"
        >
          <span className="button-icon record-icon">●</span>
          <span className="button-text">Start Recording</span>
        </button>
      ) : (
        <button
          className="record-button stop"
          onClick={onStopRecording}
          aria-label="Stop recording"
        >
          <span className="button-icon stop-icon">■</span>
          <span className="button-text">Stop Recording</span>
        </button>
      )}
    </div>
  );
};

export default RecordingControls;
