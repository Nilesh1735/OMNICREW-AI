import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import CanvasBackground from './CanvasBackground';

// Dynamic API URL for deployment
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const AuthScreen: React.FC = () => {
  const { login } = useAuth();
  const { showToast } = useToast();
  
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setIsLoading(true);

    const endpoint = isLogin ? `${API_BASE_URL}/api/auth/login` : `${API_BASE_URL}/api/auth/signup`;
    
    const payload = isLogin 
      ? { login_id: email, password } 
      : { username, email, password };

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Authentication failed');

      if (isLogin) {
        localStorage.setItem('omnicrew_token', data.token);
        login();
        showToast('Access granted. Welcome back.', 'success');
      } else {
        showToast('Account created successfully. Please log in.', 'success');
        setIsLogin(true);
        setPassword('');
        setUsername('');
      }
    } catch (err: any) {
      setErrorMessage(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-overlay">
      <CanvasBackground />
      <div className="landing-nav">
        <div className="nav-brand">OmniCrew<span>AI</span></div>
      </div>

      <div className="landing-content">
        
        <motion.div 
          className="hero-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <h1 className="hero-title glitch-text" data-text="Autonomous Web Agents.">
            Autonomous Web Agents.<br /><span className="text-red">Own Your Pipeline.</span> No Meters.
          </h1>
          <p className="hero-subtitle">
            A complete web extraction crew that runs entirely on your infrastructure. No API usage caps. No cloud dependency. Bring your engine, or run local.
          </p>
          
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem', marginTop: '2rem' }}>
            <span style={{ fontSize: '0.7rem', color: '#86868b', textTransform: 'uppercase', letterSpacing: '1px' }}>Powered By</span>
            <div style={{ display: 'flex', gap: '2rem', alignItems: 'center', opacity: 0.9 }}>
              <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#ff7000' }}>Mistral AI</span>
              <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#10a37f' }}>OpenAI</span>
              <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#ffffff' }}>Ollama (Local)</span>
              <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#2D7FF9' }}>Playwright</span>
            </div>
          </div>
        </motion.div>

        <motion.div 
          className="problem-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <div className="section-label">[01] The Problem</div>
          <h2 className="section-heading">You don't own your scraping pipeline. And you're being metered.</h2>
          <div className="problem-grid">
            <div className="problem-card">
              <div className="card-label">Vendor Lock-in</div>
              <p>They host the LLM. They host the parser. If their API goes down, your data flow stops.</p>
            </div>
            <div className="problem-card">
              <div className="card-label">Artificial Scarcity</div>
              <p>They charge you per 1,000 requests. You hesitate to run agent loops because it costs tokens.</p>
            </div>
            <div className="problem-card">
              <div className="card-label">Rigid Schemas</div>
              <p>Standard scrapers break when DOM changes. You spend hours maintaining CSS selectors.</p>
            </div>
          </div>
        </motion.div>

        <motion.div 
          className="solution-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          <div className="section-label">[02] The Solution</div>
          <h2 className="section-heading">Everything routed. Own your AI.</h2>
          <p className="solution-text">
            OmniCrew AI is a closed-loop multi-agent system. The Researcher scrapes, the Analyst extracts, the Manager validates. You route the LLM engine: OpenAI, Gemini, or 100% local Ollama. Zero API limits.
          </p>
        </motion.div>

        <motion.div 
          className="stats-strip"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.7 }}
        >
          <div className="stat-box">
            <span className="stat-label">Latency</span>
            <span className="stat-value">0ms</span>
            <span className="stat-note">No external API round-trip (Local)</span>
          </div>
          <div className="stat-box">
            <span className="stat-label">Cost / Token</span>
            <span className="stat-value">$0.00</span>
            <span className="stat-note">Run local Ollama models</span>
          </div>
          <div className="stat-box">
            <span className="stat-label">Schema</span>
            <span className="stat-value">100%</span>
            <span className="stat-note">Domain-agnostic dynamic JSON</span>
          </div>
        </motion.div>

        <motion.div 
          className="auth-terminal"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.9 }}
          style={{ 
            backgroundColor: 'rgba(20, 20, 20, 0.8)', 
            backdropFilter: 'blur(12px)', 
            border: '1px solid rgba(255, 255, 255, 0.1)' 
          }}
        >
          <div className="terminal-header">
            <span className="terminal-dots"><span></span><span></span><span></span></span>
            <span className="terminal-title">omnicrew://access</span>
          </div>
          
          <div className="auth-card-content">
            <div className="auth-tabs">
              <button className={`auth-tab ${isLogin ? 'active' : ''}`} onClick={() => { setIsLogin(true); setErrorMessage(null); }}>
                $ login
              </button>
              <button className={`auth-tab ${!isLogin ? 'active' : ''}`} onClick={() => { setIsLogin(false); setErrorMessage(null); }}>
                $ signup
              </button>
            </div>

            {errorMessage && <div className="error-banner">{errorMessage}</div>}

            <form onSubmit={handleSubmit} className="auth-form">
              {!isLogin && (
                <div className="input-group">
                  <label>[01] Username</label>
                  <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="agent_smith" required />
                </div>
              )}
              <div className="input-group">
                <label>[{isLogin ? '01' : '02'}] {isLogin ? 'Email or Username' : 'Email'}</label>
                <input type="text" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="admin@omnicrew.ai" required />
              </div>
              <div className="input-group">
                <label>[{isLogin ? '02' : '03'}] Password</label>
                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••••••" required />
              </div>
              <button type="submit" className="start-btn auth-submit-btn" disabled={isLoading}>
                {isLoading ? 'PROCESSING...' : (isLogin ? 'ACCESS_TERMINAL' : 'CREATE_ACCOUNT')}
              </button>
            </form>
          </div>
        </motion.div>

        <div className="landing-footer">
          <p>Break free from metered APIs. Bring your engine, or run local.</p>
        </div>
      </div>
    </div>
  );
};

export default AuthScreen;