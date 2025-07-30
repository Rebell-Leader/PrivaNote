import React from 'react';

interface TitleBarProps {
  onMinimize: () => void;
  onMaximize: () => void;
  onClose: () => void;
}

const TitleBar: React.FC<TitleBarProps> = ({ onMinimize, onMaximize, onClose }) => {
  return (
    <div className="title-bar">
      <div className="title-bar-left">
        <div className="app-logo">🎙️</div>
        <span className="title-text">PrivaNote</span>
      </div>
      <div className="title-bar-right">
        <button
          className="title-button minimize"
          onClick={onMinimize}
          aria-label="Minimize window"
        >
          −
        </button>
        <button
          className="title-button maximize"
          onClick={onMaximize}
          aria-label="Maximize window"
        >
          □
        </button>
        <button
          className="title-button close"
          onClick={onClose}
          aria-label="Close window"
        >
          ×
        </button>
      </div>
    </div>
  );
};

export default TitleBar;
