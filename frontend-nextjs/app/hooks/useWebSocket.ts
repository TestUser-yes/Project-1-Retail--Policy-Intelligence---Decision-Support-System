'use client';

import { useEffect, useRef, useCallback, useState } from 'react';

interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

export function useWebSocket(
  token: string | null,
  onMessage?: (message: WebSocketMessage) => void,
  onError?: (error: Error) => void,
  autoConnect: boolean = true
) {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const [isConnected, setIsConnected] = useState(false);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const MAX_RECONNECT_ATTEMPTS = 5;
  const RECONNECT_DELAY_MS = 3000;

  const connect = useCallback(() => {
    if (!token || wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
      const wsUrl = apiUrl.replace(/^http/, 'ws');
      const url = `${wsUrl}/ws/query-stream/${token}`;

      wsRef.current = new WebSocket(url);

      wsRef.current.onopen = () => {
        console.log('[WebSocket] Connected');
        setIsConnected(true);
        setReconnectAttempts(0);

        // Send subscription message
        wsRef.current?.send(JSON.stringify({
          type: 'subscribe',
          timestamp: new Date().toISOString(),
        }));
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          onMessage?.(message);
        } catch (error) {
          console.error('[WebSocket] Failed to parse message:', error);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('[WebSocket] Error:', error);
        onError?.(new Error('WebSocket connection error'));
      };

      wsRef.current.onclose = () => {
        console.log('[WebSocket] Disconnected');
        setIsConnected(false);

        // Attempt reconnection
        if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
          const delay = RECONNECT_DELAY_MS * Math.pow(2, reconnectAttempts);
          reconnectTimeoutRef.current = setTimeout(() => {
            setReconnectAttempts((prev) => prev + 1);
            connect();
          }, delay);
        } else {
          onError?.(new Error('Failed to reconnect after multiple attempts'));
        }
      };
    } catch (error) {
      console.error('[WebSocket] Connection failed:', error);
      onError?.(error as Error);
    }
  }, [token, onMessage, onError, reconnectAttempts]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  const send = useCallback((message: WebSocketMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('[WebSocket] Not connected, cannot send message');
    }
  }, []);

  const sendPing = useCallback(() => {
    send({
      type: 'ping',
      timestamp: new Date().toISOString(),
    });
  }, [send]);

  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return {
    isConnected,
    send,
    sendPing,
    disconnect,
    connect,
    reconnectAttempts,
  };
}
