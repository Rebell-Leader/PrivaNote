import React from 'react';
import RecordingControls from './RecordingControls';
import StatusIndicator from './StatusIndicator';

interface ControlPanelProps {
  isRecording: boolean;
  status: string;
  onStartRecording: () => void;
  onStopRecording: () => void;
}

const ControlPanel: React.FC<ControlPanelProps> = ({
  isRecording,
  status,
  onStartRecording,
  onStopRecording,
}) => {
  return (
    <div className="control-panel">
      <StatusIndicator isRecording={isRecording} status={status} />
      <RecordingControls
        isRecording={isRecording}
        onStartRecording={onStartRecording}
        onStopRecording={onStopRecording}
      />
    </div>
  );
};

export default ControlPanel;
