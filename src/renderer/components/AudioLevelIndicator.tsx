import React from 'react';

interface AudioLevelIndicatorProps {
  level: number; // 0-100
  label: string;
  isActive: boolean;
}

const AudioLevelIndicator: React.FC<AudioLevelIndicatorProps> = ({
  level,
  label,
  isActive,
}) => {
  const normalizedLevel = Math.max(0, Math.min(100, level));
  const barCount = 10;
  const activeBars = Math.ceil((normalizedLevel / 100) * barCount);

  return (
    <div className={`audio-level-indicator ${isActive ? 'active' : 'inactive'}`}>
      <div className="audio-level-label">{label}</div>
      <div className="audio-level-bars">
        {Array.from({ length: barCount }, (_, index) => {
          const isBarActive = index < activeBars && isActive;
          const barLevel = index / (barCount - 1);
          let barClass = 'audio-bar';

          if (isBarActive) {
            if (barLevel < 0.6) {
              barClass += ' low';
            } else if (barLevel < 0.8) {
              barClass += ' medium';
            } else {
              barClass += ' high';
            }
          }

          return (
            <div
              key={index}
              className={barClass}
              style={{
                opacity: isBarActive ? 1 : 0.2,
              }}
            />
          );
        })}
      </div>
      <div className="audio-level-value">
        {isActive ? `${Math.round(normalizedLevel)}%` : '--'}
      </div>
    </div>
  );
};

export default AudioLevelIndicator;
