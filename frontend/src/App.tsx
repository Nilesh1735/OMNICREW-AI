import React, { useState, useEffect, useRef } from 'react';
import LogViewer from './components/LogViewer';
import LeadTable from './components/LeadTable';
import AuthScreen from './components/AuthScreen';
import PipelineGraph from './components/PipelineGraph';
import ErrorBoundary from './components/ErrorBoundary';
import CanvasBackground from './components/CanvasBackground';
import Admin from './pages/Admin';
import { useLeads } from './hooks/useLeads';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider, useToast } from './context/ToastContext';

// DYNAMIC API URL: Uses Vercel env var in production, falls back to localhost for dev
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_BASE_URL = API_BASE_URL.replace('http', 'ws');

interface AgentLog {
  agent_name: string;
  action: string;
  thought_process: string;
}

const Dashboard: React.FC = () => {
  const { logout } = useAuth();
  const { showToast } = useToast();
  const { leads, isLoading } = useLeads();
  
  const [taskDescription, setTaskDescription] = useState('Find the title and points of the top story on Hacker News.');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [vignette, setVignette] = useState<'success' | 'error' | null>(null);
  const [logs, setLogs] = useState<AgentLog[]>([]);
  const [status, setStatus] = useState<'connected' | 'disconnected'>('connected');
  
  const btnRef = useRef<HTMLButtonElement>(null);
  const dashboardRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!btnRef.current) return;
    const rect = btnRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    btnRef.current.style.transform = `translate(${x * 0.2}px, ${y * 0.2}px)`;
  };

  const handleMouseLeave = () => {
    if (btnRef.current) btnRef.current.style.transform = 'translate(0px, 0px)';
  };

  const handleParallax = (e: React.MouseEvent) => {
    if (!dashboardRef.current) return;
    const cards = dashboardRef.current.querySelectorAll('.bento-card');
    const xVal = (e.clientX / window.innerWidth - 0.5) * 8;
    const yVal = (e.clientY / window.innerHeight - 0.5) * -8;
    cards.forEach((card) => {
      (card as HTMLElement).style.transform = `perspective(1000px) rotateY(${xVal}deg) rotateX(${yVal}deg)`;
    });
  };

  const handleParallaxLeave = () => {
    if (!dashboardRef.current) return;
    const cards = dashboardRef.current.querySelectorAll('.bento-card');
    cards.forEach((card) => {
      (card as HTMLElement).style.transform = `perspective(1000px) rotateY(0deg) rotateX(0deg)`;
    });
  };

  useEffect(() => {
    if (logs.length > 0) {
      const lastLog = logs[logs.length - 1];
      if (
        lastLog.action === "Task Completed" || 
        lastLog.action === "Saved" || 
        lastLog.action === "Error" || 
        lastLog.action === "Task Failed"
      ) {
        setIsSubmitting(false);
        
        if (lastLog.action === "Task Failed" || lastLog.action === "Error") {
          showToast('Pipeline halted. Check telemetry.', 'error');
          setVignette('error');
        } else {
          showToast('Extraction sequence finished.', 'success');
          setVignette('success');
        }
        
        setTimeout(() => setVignette(null), 1200);
        if (wsRef.current) wsRef.current.close();
      }
    }
  }, [logs, showToast]);

  const startTask = async () => {
    setError(null);
    setIsSubmitting(true);
    setLogs([]);
    try {
      const response = await fetch(`${API_BASE_URL}/api/webhook/start-task`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('omnicrew_token') || 'no_token'}`
        },
        body: JSON.stringify({ task_description: taskDescription })
      });
      
      const data = await response.json();
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
      showToast('Autonomous extraction initiated...', 'success');
      
      if (wsRef.current) wsRef.current.close();
      
      const ws = new WebSocket(`${WS_BASE_URL}/ws/logs`);
      wsRef.current = ws;
      
      ws.onopen = () => {
        setStatus('connected');
        ws.send(data.task_id);
      };
      
      ws.onmessage = (event) => {
        try {
          const logData = JSON.parse(event.data);
          setLogs((prevLogs) => [...prevLogs, logData]);
        } catch (e) {
          console.error("Failed to parse log data", e);
        }
      };
      
      ws.onclose = () => setStatus('disconnected');
      ws.onerror = () => setStatus('disconnected');
      
    } catch (err: any) {
      console.error('Failed to start task:', err);
      setError(`Failed to connect to backend: ${err.message}`);
      showToast(`Failed to start task: ${err.message}`, 'error');
      setIsSubmitting(false);
    }
  };

  const statusText = status === 'connected' ? 'SYSTEM_ONLINE' : 'OFFLINE';

  return (
    <div className="dashboard-container" ref={dashboardRef} onMouseMove={handleParallax} onMouseLeave={handleParallaxLeave}>
      <CanvasBackground />
      
      <div className={`vignette-overlay ${vignette === 'success' ? 'vignette-success vignette-active' : ''}`}></div>
      <div className={`vignette-overlay ${vignette === 'error' ? 'vignette-error vignette-active' : ''}`}></div>

      <header className="bento-header">
        <div className="brand">
          <h1>OmniCrew<span>AI</span></h1>
          <p className="tagline">Sovereign Data Extraction. No Cloud Limits.</p>
        </div>
        <div className="flex-row">
          <div className="status-indicator">
            <span className={`status-dot ${status === 'connected' ? 'connected' : 'disconnected'}`}></span>
            {statusText}
          </div>
          <button onClick={() => window.location.href = '?view=history'} className="logout-btn" style={{ marginRight: '10px' }}>History</button>
          <button onClick={logout} className="logout-btn">Disconnect</button>
        </div>
      </header>

      {/* BULLETPROOF 80/20 FLEX LAYOUT */}
      <div className="bento-card" style={{ display: 'flex', flexDirection: 'row', alignItems: 'flex-end', gap: '15px', width: '100%', boxSizing: 'border-box' }}>
        
        <div style={{ flex: '1 1 80%', display: 'flex', flexDirection: 'column', minWidth: 0 }}>
          <label style={{ color: '#86868b', fontSize: '0.8rem', marginBottom: '5px' }}>[01] Target_Query</label>
          <input 
            type="text" 
            value={taskDescription} 
            onChange={(e) => setTaskDescription(e.target.value)} 
            placeholder="e.g., Find the top 2 AI startups in Bangalore" 
            style={{ width: '100%', padding: '12px', backgroundColor: '#1c1c1c', border: '1px solid #333', borderRadius: '4px', color: '#fff', boxSizing: 'border-box' }}
          />
        </div>
        
        <button 
          ref={btnRef}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
          className="start-btn" 
          onClick={startTask} 
          disabled={isSubmitting}
          style={{ 
            flex: '0 0 auto', 
            height: '45px', 
            marginBottom: '0',
            whiteSpace: 'nowrap',
            padding: '0 30px'
          }}
        >
          {isSubmitting ? (<><span className="spinner"></span> EXECUTING...</>) : 'INITIATE_CREW'}
        </button>
        
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="bento-card pipeline-container">
        <div className="section-header">
          <h3>[02] Pipeline_Telemetry</h3>
          {isSubmitting && <span className="processing-badge">DATA_FLOW_ACTIVE</span>}
        </div>
        <PipelineGraph logs={logs} isProcessing={isSubmitting} />
      </div>

      <main className="dashboard-grid">
        <section className={`bento-card ${isSubmitting ? 'scanning' : ''}`}>
          <div className="section-header">
            <h3>[03] Agent_Reasoning_Feed</h3>
          </div>
          <LogViewer logs={logs} />
          {isSubmitting && <div className="scan-line"></div>}
        </section>
        
        <section className={`bento-card ${isSubmitting ? 'scanning' : ''}`}>
          <div className="section-header">
            <h3>[04] Extracted_Entities</h3>
          </div>
          <LeadTable leads={leads} isLoading={isLoading} />
          {isSubmitting && <div className="scan-line"></div>}
        </section>
      </main>
    </div>
  );
};

const HistoryView: React.FC = () => {
  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/tasks/history`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('omnicrew_token') || 'no_token'}` }
        });
        const data = await res.json();
        setTasks(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  return (
    <div className="dashboard-container">
      <CanvasBackground />
      <header className="bento-header">
        <div className="brand">
          <h1>OmniCrew<span>AI</span></h1>
          <p className="tagline">Task History</p>
        </div>
        <button onClick={() => window.location.href = '/'} className="logout-btn">Back to Dashboard</button>
      </header>
      
      <div className="bento-card" style={{ padding: '2rem' }}>
        {loading ? <p>Loading history...</p> : tasks.length === 0 ? <p>No tasks found.</p> : (
          <table style={{ width: '100%', color: '#fff' }}>
            <thead>
              <tr>
                <th style={{ textAlign: 'left', padding: '10px' }}>Task ID</th>
                <th style={{ textAlign: 'left', padding: '10px' }}>Description</th>
                <th style={{ textAlign: 'left', padding: '10px' }}>Status</th>
                <th style={{ textAlign: 'left', padding: '10px' }}>Created At</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map(task => (
                <tr key={task.id} style={{ borderBottom: '1px solid #333' }}>
                  <td style={{ padding: '10px' }}>{task.id.substring(0, 8)}...</td>
                  <td style={{ padding: '10px' }}>{task.description}</td>
                  <td style={{ padding: '10px' }}>{task.status}</td>
                  <td style={{ padding: '10px' }}>{new Date(task.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

const RootApp: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const params = new URLSearchParams(window.location.search);
  const view = params.get('view');

  return (
    <ErrorBoundary>
      {!isAuthenticated ? (
        <AuthScreen />
      ) : view === 'admin' ? (
        <Admin />
      ) : view === 'history' ? (
        <HistoryView />
      ) : (
        <Dashboard />
      )}
    </ErrorBoundary>
  );
};

const App: React.FC = () => (
  <ToastProvider>
    <AuthProvider>
      <RootApp />
    </AuthProvider>
  </ToastProvider>
);

export default App;