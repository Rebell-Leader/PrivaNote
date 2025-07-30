import React from 'react';

interface ProgressIndicatorProps {
  isVisible: boolean;
  progress?: number; // 0-100
  message?: string;
  type?: 'indeterminate' | 'determinate';
}

const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  isVisible,
  progress = 0,
  message = 'Processing...',
  type = 'indeterminate',
}) => {
  if (!isVisible) return null;

  return (
    <div className="progress-indicator">
      <div className="progress-content">
        <div className="progress-message">{message}</div>
        <div className="progress-bar-container">
          <div className={`progress-bar ${type}`}>
            {type === 'determinate' && (
              <div
                className="progress-fill"
                style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
              />
            )}
            {type === 'indeterminate' && (
              <div className="progress-fill indeterminate" />
            )}
          </div>
        </div>
        {type === 'determinate' && (
          <div className="progress-percentage">{Math.round(progress)}%</div>
        )}
      </div>
    </div>
  );
};

export default ProgressIndicator;
