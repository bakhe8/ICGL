import { motion } from 'framer-motion';
import { Activity, Zap } from 'lucide-react';
import { useEffect, useState } from 'react';

type BusEvent = {
    id: string;
    topic: string;
    sender: string;
    timestamp: number;
    intensity: number; // 0-1
};

export default function NervousSystemMonitor() {
    const [events, setEvents] = useState<BusEvent[]>([]);

    // Live Data Integration via SSE
    useEffect(() => {
        const es = new EventSource('/api/pulse/stream');

        es.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                // Parse the nested JSON data string if it comes as double-encoded
                const parsed = typeof data === 'string' ? JSON.parse(data) : data;

                const newEvent: BusEvent = {
                    id: parsed.id || Math.random().toString(36),
                    topic: parsed.topic || 'unknown',
                    sender: parsed.sender || 'system',
                    timestamp: parsed.timestamp || Date.now(),
                    intensity: 0.8, // Dynamic intensity based on priority?
                };

                setEvents((prev) => [newEvent, ...prev].slice(0, 50));
            } catch (e) {
                console.error("Pulse Error:", e);
            }
        };

        es.onerror = (err) => {
            console.error("Nervous System Connection Lost", err);
            es.close();
        };

        return () => es.close();
    }, []);

    return (
        <div className="glass rounded-3xl p-6 relative overflow-hidden min-h-[300px] flex flex-col">
            <header className="flex items-center justify-between mb-6 z-10 relative">
                <div>
                    <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                        <Activity className="w-5 h-5 text-rose-500" />
                        Nervous System Activity
                    </h2>
                    <p className="text-xs text-slate-500">Real-time Event Bus Traffic (backend/core/bus.py)</p>
                </div>
                <div className="flex items-center gap-2">
                    <span className="relative flex h-3 w-3">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-rose-500"></span>
                    </span>
                    <span className="text-xs font-mono text-rose-600">LIVE</span>
                </div>
            </header>

            {/* ECG Visualizer */}
            <div className="absolute inset-0 top-16 opacity-10 pointer-events-none">
                <svg viewBox="0 0 400 100" className="w-full h-full" preserveAspectRatio="none">
                    <motion.path
                        d="M0 50 L20 50 L25 30 L35 70 L40 50 L60 50 L65 10 L75 90 L80 50 L100 50 L105 40 L115 60 L120 50 L400 50"
                        fill="none"
                        stroke="#f43f5e"
                        strokeWidth="2"
                        initial={{ pathLength: 0, x: -400 }}
                        animate={{ pathLength: 1, x: 0 }}
                        transition={{
                            duration: 2,
                            repeat: Infinity,
                            ease: "linear",
                            repeatType: "loop"
                        }}
                    />
                </svg>
            </div>

            {/* Event Stream */}
            <div className="flex-1 space-y-3 z-10 relative overflow-y-auto custom-scrollbar pr-2 h-full">
                {events.map((ev) => (
                    <motion.div
                        key={ev.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex items-center justify-between p-3 rounded-xl bg-white/60 border border-slate-100 shadow-sm backdrop-blur-sm"
                    >
                        <div className="flex items-center gap-3">
                            <div className={`p-2 rounded-lg ${ev.topic.includes('security') ? 'bg-rose-100 text-rose-600' :
                                ev.topic.includes('core') ? 'bg-blue-100 text-blue-600' :
                                    'bg-violet-100 text-violet-600'
                                }`}>
                                <Zap className="w-3 h-3" />
                            </div>
                            <div>
                                <p className="text-xs font-bold text-slate-700 font-mono">{ev.topic}</p>
                                <p className="text-[10px] text-slate-400">{ev.sender}</p>
                            </div>
                        </div>
                        <span className="text-[10px] font-mono text-slate-400">
                            {new Date(ev.timestamp).toLocaleTimeString().split(' ')[0]}
                        </span>
                    </motion.div>
                ))}
            </div>

            {/* Background Pulse */}
            <div className="absolute -right-20 -bottom-20 w-64 h-64 bg-rose-500/5 rounded-full blur-3xl animate-pulse"></div>
        </div>
    );
}
