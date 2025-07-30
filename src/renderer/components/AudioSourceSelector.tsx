import React, { useState, useEffect } from 'react';

interface AudioSource {
  id: string;
  label: string;
  type: 'microphone' | 'system' | 'screen';
  deviceId?: string;
}

interface AudioSourceSelectorProps {
  isVisible: boolean;
  onSourcesSelected: (sources: { microphone: boolean; systemAudio: boolean; selectedMicId?: string }) => void;
  onClose: () => void;
  getAvailableSources: () => Promise<AudioSource[]>;
}

const AudioSourceSelector: React.FC<AudioSourceSelectorProps> = ({
  isVisible,
  onSourcesSelected,
  onClose,
  getAvailableSources,
}) => {
  const [sources, setSources] = useState<AudioSource[]>([]);
  const [selectedMicrophone, setSelectedMicrophone] = useState<string>('');
  const [captureMicrophone, setCaptureMicrophone] = useState<boolean>(true);
  const [captureSystemAudio, setCaptureSystemAudio] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    if (isVisible) {
      loadSources();
    }
  }, [isVisible]);

  const loadSources = async () => {
    setLoading(true);
    try {
      const availableSources = await getAvailableSources();
      setSources(availableSources);

      // Auto-select the first microphone
      const firstMic = availableSources.find(s => s.type === 'microphone');
      if (firstMic) {
        setSelectedMicrophone(firstMic.id);
      }
    } catch (error) {
      console.error('Failed to load audio sources:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = () => {
    onSourcesSelected({
      microphone: captureMicrophone,
      systemAudio: captureSystemAudio,
      selectedMicId: captureMicrophone ? selectedMicrophone : undefined,
    });
    onClose();
  };

  if (!isVisible) return null;

  const microphones = sources.filter(s => s.type === 'microphone');
  const hasSystemAudio = sources.some(s => s.type === 'system' || s.type === 'screen');

  return (
    <div className="audio-source-selector-overlay">
      <div className="audio-source-selector">
        <div className="audio-source-header">
          <h3>Select Audio Sources</h3>
          <button className="close-button" onClick={onClose} aria-label="Close">
            ×
          </button>
        </div>

        <div className="audio-source-content">
          {loading ? (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Loading audio sources...</p>
            </div>
          ) : (
            <>
              <div className="source-section">
                <div className="source-option">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={captureMicrophone}
                      onChange={(e) => setCaptureMicrophone(e.target.checked)}
                    />
                    <span className="checkmark"></span>
                    Capture Microphone
                  </label>
                  <p className="source-description">
                    Record your voice and any audio picked up by your microphone
                  </p>
                </div>

                {captureMicrophone && microphones.length > 0 && (
                  <div className="microphone-selector">
                    <label htmlFor="mic-select">Select Microphone:</label>
                    <select
                      id="mic-select"
                      value={selectedMicrophone}
                      onChange={(e) => setSelectedMicrophone(e.target.value)}
                    >
                      {microphones.map(mic => (
                        <option key={mic.id} value={mic.id}>
                          {mic.label}
                        </option>
                      ))}
                    </select>
                  </div>
                )}
              </div>

              <div className="source-section">
                <div className="source-option">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={captureSystemAudio}
                      onChange={(e) => setCaptureSystemAudio(e.target.checked)}
                      disabled={!hasSystemAudio}
                    />
                    <span className="checkmark"></span>
                    Capture System Audio
                  </label>
                  <p className="source-description">
                    Record audio from applications (Zoom, Teams, music, etc.)
                    {!hasSystemAudio && (
                      <span className="not-supported"> - Not supported in this browser</span>
                    )}
                  </p>
                </div>

                {captureSystemAudio && hasSystemAudio && (
                  <div className="system-audio-info">
                    <div className="info-box">
                      <strong>Note:</strong> System audio capture requires screen sharing permission.
                      You'll be prompted to select a screen or application to share. The video will be
                      discarded - only the audio will be recorded.
                    </div>
                  </div>
                )}
              </div>

              {!captureMicrophone && !captureSystemAudio && (
                <div className="warning-box">
                  <strong>Warning:</strong> You must select at least one audio source to record.
                </div>
              )}
            </>
          )}
        </div>

        <div className="audio-source-actions">
          <button
            className="primary-button"
            onClick={handleConfirm}
            disabled={loading || (!captureMicrophone && !captureSystemAudio)}
          >
            Start Recording
          </button>
          <button className="secondary-button" onClick={onClose}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default AudioSourceSelector;
