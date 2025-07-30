import React from 'react';

interface PermissionsDialogProps {
  isVisible: boolean;
  permissions: {
    microphone: boolean;
    system: boolean;
    error?: string;
  };
  onRequestPermissions: () => void;
  onClose: () => void;
}

const PermissionsDialog: React.FC<PermissionsDialogProps> = ({
  isVisible,
  permissions,
  onRequestPermissions,
  onClose,
}) => {
  if (!isVisible) return null;

  const hasMissingPermissions = !permissions.microphone || !permissions.system;

  return (
    <div className="permissions-dialog-overlay">
      <div className="permissions-dialog">
        <div className="permissions-dialog-header">
          <h3>Audio Permissions Required</h3>
          <button className="close-button" onClick={onClose} aria-label="Close">
            ×
          </button>
        </div>

        <div className="permissions-dialog-content">
          <p>PrivaNote needs access to your audio devices to record meetings:</p>

          <div className="permission-item">
            <div className={`permission-status ${permissions.microphone ? 'granted' : 'denied'}`}>
              {permissions.microphone ? '✓' : '✗'}
            </div>
            <div className="permission-details">
              <strong>Microphone Access</strong>
              <p>Required to capture your voice during meetings</p>
            </div>
          </div>

          <div className="permission-item">
            <div className={`permission-status ${permissions.system ? 'granted' : 'denied'}`}>
              {permissions.system ? '✓' : '✗'}
            </div>
            <div className="permission-details">
              <strong>System Audio Access</strong>
              <p>Required to capture audio from meeting applications</p>
            </div>
          </div>

          {permissions.error && (
            <div className="permission-error">
              <strong>Error:</strong> {permissions.error}
            </div>
          )}

          {hasMissingPermissions && (
            <div className="permission-instructions">
              <h4>How to grant permissions:</h4>
              <ol>
                <li>Click "Request Permissions" below</li>
                <li>Allow access when prompted by your browser/system</li>
                <li>For system audio, you may need to enable "Stereo Mix" in Windows sound settings</li>
              </ol>
            </div>
          )}
        </div>

        <div className="permissions-dialog-actions">
          {hasMissingPermissions ? (
            <button className="primary-button" onClick={onRequestPermissions}>
              Request Permissions
            </button>
          ) : (
            <button className="primary-button" onClick={onClose}>
              Continue
            </button>
          )}
          <button className="secondary-button" onClick={onClose}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default PermissionsDialog;
