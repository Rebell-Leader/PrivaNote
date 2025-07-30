import React from 'react';

interface HeaderProps {
  appVersion: string;
}

const Header: React.FC<HeaderProps> = ({ appVersion }) => {
  return (
    <header className="header">
      <div className="header-content">
        <h1 className="app-title">PrivaNote</h1>
        <span className="app-version">v{appVersion}</span>
        <p className="app-description">Privacy-focused AI meeting assistant with local processing</p>
      </div>
    </header>
  );
};

export default Header;
