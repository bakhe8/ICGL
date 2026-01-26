import { resolveWsUrl } from '@web-src/client';
import type { TimelineEvent } from '@web-src/state/cockpitStore';
import useCockpitStore from '@web-src/state/cockpitStore';
import { useEffect, useRef, useState } from 'react';

const bootstrapEvents: TimelineEvent[] = [
  {
    id: 'boot',
    time: new Date().toISOString(),
    label: 'تم تشغيل المراقبة المستمرة (SCP WebSocket)',
    source: 'Sentinel',
    severity: 'info',
  },
  {
    id: 'policy',
    time: new Date(Date.now() - 3 * 60 * 1000).toISOString(),
    label: 'حفظ قرار سيادي: تحديث سياسة الامتثال P-OPS-05',
    source: 'Policy Agent',
    severity: 'info',
  },
];

export function useSCPStream() {
  const { pushTimeline, timeline, setTimeline } = useCockpitStore();
  const [connection, setConnection] = useState<'connecting' | 'open' | 'closed'>('connecting');
  const hasSeeded = useRef(false);

  useEffect(() => {
    if (!hasSeeded.current) {
      if (!timeline?.length) {
        setTimeline(bootstrapEvents);
      }
      hasSeeded.current = true;
    }
    let socket: WebSocket | undefined;
    let isMounted = true;

    const connect = () => {
      try {
        const wsUrl = resolveWsUrl('/ws/scp');
        console.log(`[SCP] Connecting to ${wsUrl}...`);
        socket = new WebSocket(wsUrl);

        socket.onopen = () => {
          if (isMounted) setConnection('open');
          console.log('[SCP] Connected');
        };

        socket.onerror = (e) => {
          if (isMounted) {
            // Only log real errors, not formatted "type: error" events without detail
            console.debug('[SCP] WebSocket event:', e);
            setTimeout(() => setConnection('closed'), 0);
          }
        };

        socket.onclose = (e) => {
          if (isMounted) {
            setTimeout(() => setConnection('closed'), 0);
            if (e.code !== 1000) {
              console.log('[SCP] Disconnected', e.code, e.reason);
            }
          }
        };

        socket.onmessage = (event) => {
          if (!isMounted) return;
          try {
            const payload = JSON.parse(event.data);
            if (payload?.type === 'alert' || payload?.event_type) {
              const entry: TimelineEvent = {
                id: payload.alert_id || payload.id || crypto.randomUUID(),
                time: payload.timestamp ? new Date().toISOString() : new Date().toISOString(),
                label: payload.message || payload.description || 'حدث جديد من قناة المراقبة',
                source: payload.source || 'SCP',
                severity:
                  payload.severity && ['info', 'warn', 'critical'].includes(payload.severity)
                    ? payload.severity
                    : 'info',
              };
              pushTimeline(entry);
            }
          } catch {
            // Ignore malformed frames
          }
        };
      } catch (err) {
        console.error('[SCP] Init Error:', err);
        if (isMounted) setTimeout(() => setConnection('closed'), 0);
      }
    };

    // Debounce connection to handle React Strict Mode double-mount
    const connectTimer = window.setTimeout(connect, 100);

    return () => {
      isMounted = false;
      window.clearTimeout(connectTimer);
      if (socket) {
        socket.close();
      }
    };
  }, [pushTimeline, setTimeline, timeline]);

  return {
    connection,
    timeline: timeline?.length ? timeline : bootstrapEvents,
  };
}
