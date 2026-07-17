import { useEffect, useState, useRef, useCallback } from 'react';
import { AgentLog } from '../types';

const WS_URL = 'ws://localhost:8000/ws/logs';

type ConnectionStatus = 'connected' | 'disconnected' | 'reconnecting';

export const useWebSocket = () => {
  const [logs, setLogs] = useState<AgentLog[]>([]);
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const manualCloseRef = useRef<boolean>(false);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    setStatus('reconnecting');
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      setStatus('connected');
      manualCloseRef.current = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };

    ws.onmessage = (event) => {
      try {
        const log: AgentLog = JSON.parse(event.data);
        setLogs((prev) => [...prev.slice(-50), log]); // Keep last 50 logs
      } catch (e) {
        console.error('Failed to parse WebSocket message', e);
      }
    };

    ws.onclose = () => {
      setStatus('disconnected');
      if (!manualCloseRef.current) {
        // Attempt to reconnect every 5 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('Attempting to reconnect WebSocket...');
          connect();
        }, 5000);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error', error);
      ws.close(); // Trigger onclose for reconnect logic
    };
  }, []);

  useEffect(() => {
    connect();

    return () => {
      manualCloseRef.current = true;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  return { logs, status };
};