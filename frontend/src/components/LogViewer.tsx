import React, { useEffect, useRef, useState } from 'react';
import { AgentLog } from '../types';

interface LogViewerProps {
  logs: AgentLog[];
}

// Typewriter component for streaming text
const Typewriter: React.FC<{ text: string }> = ({ text }) => {
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(true);

  useEffect(() => {
    let i = 0;
    setDisplayedText('');
    setIsTyping(true);
    
    // Only type if there is text
    if (!text) {
      setIsTyping(false);
      return;
    }

    const interval = setInterval(() => {
      if (i < text.length) {
        setDisplayedText(text.substring(0, i + 1));
        i++;
      } else {
        clearInterval(interval);
        setIsTyping(false);
      }
    }, 15); // Typing speed (15ms per char)

    return () => clearInterval(interval);
  }, [text]);

  return (
    <span>
      {displayedText}
      {isTyping && <span className="typewriter-cursor"></span>}
    </span>
  );
};

const LogViewer: React.FC<LogViewerProps> = ({ logs }) => {
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs]);

  return (
    <div className="log-viewer">
      <div className="log-list">
        {logs.length === 0 ? (
          <p className="empty-state">Waiting for agent activity...</p>
        ) : (
          logs.map((log, index) => {
            // Apply typewriter effect to the thought process of the LATEST log
            const isLatest = index === logs.length - 1;
            
            return (
              <div key={index} className={`log-entry log-${log.action.toLowerCase().replace(/\s+/g, '')}`}>
                <span className="log-timestamp">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </span>
                <span className="log-agent">{log.agent_name}</span>
                <span className="log-action">{log.action}</span>
                {log.thought_process && (
                  <p className="log-thought">
                    {isLatest ? <Typewriter text={log.thought_process} /> : log.thought_process}
                  </p>
                )}
              </div>
            );
          })
        )}
        <div ref={logEndRef} />
      </div>
    </div>
  );
};

export default LogViewer;