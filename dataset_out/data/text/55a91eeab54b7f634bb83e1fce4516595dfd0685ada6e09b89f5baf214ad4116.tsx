import { useEffect, useRef, useState } from 'react';

type McpStatus = 'online' | 'offline' | 'unknown';

export default function useMcpStatus(initialInterval = 5000) {
  const [status, setStatus] = useState<McpStatus>('unknown');
  const intervalRef = useRef<number>(initialInterval);
  const timeoutId = useRef<number | null>(null);

  useEffect(() => {
    let mounted = true;

    async function check() {
      try {
        const res = await fetch('/api/mcp/status', { cache: 'no-store' });
        if (!mounted) return;
        if (res.ok) {
          const json = await res.json();
          if (json && json.status === 'online') {
            setStatus('online');
            intervalRef.current = initialInterval; // reset backoff
          } else {
            setStatus('offline');
            intervalRef.current = Math.min(intervalRef.current * 2, 60000);
          }
        } else {
          setStatus('offline');
          intervalRef.current = Math.min(intervalRef.current * 2, 60000);
        }
      } catch (e) {
        if (!mounted) return;
        setStatus('offline');
        intervalRef.current = Math.min(intervalRef.current * 2, 60000);
      }

      if (!mounted) return;
      timeoutId.current = window.setTimeout(check, intervalRef.current);
    }

    check();

    return () => {
      mounted = false;
      if (timeoutId.current) {
        clearTimeout(timeoutId.current);
      }
    };
  }, [initialInterval]);

  return { status, isOnline: status === 'online' };
}
