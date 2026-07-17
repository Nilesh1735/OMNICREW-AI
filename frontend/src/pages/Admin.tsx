import React from 'react';
import CanvasBackground from '../components/CanvasBackground';

const Admin: React.FC = () => {
  // Replace with your actual LangSmith project URL
  const langsmithUrl = "https://smith.langchain.com/projects/p/omnicrew-ai-prod";

  return (
    <div className="dashboard-container">
      <CanvasBackground />
      
      <header className="bento-header">
        <div className="brand">
          <h1>OmniCrew<span>AI</span></h1>
          <p className="tagline">LLMOps Telemetry Dashboard</p>
        </div>
        <div className="flex-row">
          <a href="http://localhost:3000" className="logout-btn" style={{ textDecoration: 'none' }}>
            Back to App
          </a>
        </div>
      </header>

      <div className="bento-card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
        <div className="section-label" style={{ marginBottom: '2rem' }}>[01] LangSmith Integration</div>
        <h2 className="section-heading" style={{ fontSize: '2.5rem', marginBottom: '1.5rem' }}>
          Observability & Trace Engine
        </h2>
        <p style={{ fontSize: '1.1rem', color: '#86868b', maxWidth: '600px', margin: '0 auto 3rem auto', lineHeight: 1.6 }}>
          LangSmith actively blocks embedding inside iframes for security. Click below to open the live execution graph, token usage metrics, and agent thought traces in a secure new tab.
        </p>
        
        <a 
          href={langsmithUrl} 
          target="_blank" 
          rel="noopener noreferrer"
          className="start-btn"
          style={{ 
            display: 'inline-flex', 
            textDecoration: 'none', 
            padding: '1rem 3rem', 
            fontSize: '1rem',
            clipPath: 'none',
            borderRadius: '2px'
          }}
        >
          Launch LangSmith Dashboard →
        </a>
      </div>
    </div>
  );
};

export default Admin;