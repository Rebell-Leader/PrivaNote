import React from 'react';
import RecordingControls from './RecordingControls';
import StatusIndicator from './StatusIndicator';
import AudioLevelIndicator from './AudioLevelIndicator';

interface AudioLevels {
  microphone: number;
  system: number;
  timestamp: number;
}

interface ControlPanelProps {
  isRecording: boolean;
  status: string;
  audioLevels: AudioLevels;
  onStartRecording: () => void;
  onStopRecording: () => void;
}

const ControlPanel: React.FC<ControlPanelProps> = ({
  isRecording,
  status,
  audioLevels,
  onStartRecording,
  onStopRecording,
}) => {
  return (
    <div className="control-panel">
      <StatusIndicator isRecording={isRecording} status={status} />

      <div className="audio-levels-container">
        <AudioLevelIndicator
          level={audioLevels.microphone}
          label="Microphone"
          isActive={isRecording}
        />
        <AudioLevelIndicator
          level={audioLevels.system}
          label="System Audio"
          isActive={isRecording}
        />
      </div>

      <RecordingControls
        isRecording={isRecording}
        onStartRecording={onStartRecording}
        onStopRecording={onStopRecording}
      />
    </div>
  );
};

export default ControlPanel;
