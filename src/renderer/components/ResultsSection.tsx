import React from 'react';

interface ResultsSectionProps {
  hasResults: boolean;
  isProcessing: boolean;
}

const ResultsSection: React.FC<ResultsSectionProps> = ({ hasResults, isProcessing }) => {
  const renderContent = () => {
    if (isProcessing) {
      return (
        <div className="results-processing">
          <div className="processing-spinner"></div>
          <h3>Processing your recording...</h3>
          <p>Transcribing audio and generating AI insights</p>
        </div>
      );
    }

    if (hasResults) {
      return (
        <div className="results-tabs">
          <div className="tab-navigation">
            <button className="tab-button active">Transcript</button>
            <button className="tab-button">Summary</button>
            <button className="tab-button">Action Items</button>
            <button className="tab-button">Key Decisions</button>
          </div>
          <div className="tab-content">
            <div className="results-placeholder">
              <p>Results will be displayed here after processing</p>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="results-empty">
        <div className="empty-state-icon">🎙️</div>
        <h3>Ready to capture your meeting</h3>
        <p>Click "Start Recording" to begin transcribing and analyzing your meeting with local AI</p>
        <div className="features-list">
          <div className="feature-item">
            <span className="feature-icon">🔒</span>
            <span>100% Private - All processing happens locally</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">🤖</span>
            <span>AI-powered summaries and action items</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">📝</span>
            <span>Export to Markdown for easy sharing</span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="results-section">
      {renderContent()}
    </div>
  );
};

export default ResultsSection;
