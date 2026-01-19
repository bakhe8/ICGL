import { useEffect, useState } from 'react';
import { resolveWsUrl } from '../api/client';
import useCockpitStore from '../state/cockpitStore';
import type { TimelineEvent } from '../state/cockpitStore';

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

  useEffect(() => {
    setTimeline(bootstrapEvents);
    let socket: WebSocket | undefined;

    try {
      socket = new WebSocket(resolveWsUrl('/ws/scp'));
      socket.onopen = () => setConnection('open');
      socket.onerror = () => setConnection('closed');
      socket.onclose = () => setConnection('closed');
      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload?.type === 'alert' || payload?.event_type) {
            const entry: TimelineEvent = {
              id: payload.alert_id || payload.id || crypto.randomUUID(),
              time: payload.timestamp || new Date().toISOString(),
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
          // Ignore malformed frames; keep stream alive
        }
      };
    } catch {
      setConnection('closed');
    }

    return () => {
      setConnection('closed');
      socket?.close();
    };
  }, [pushTimeline, setTimeline]);

  return {
    connection,
    timeline: timeline.length ? timeline : bootstrapEvents,
  };
}
