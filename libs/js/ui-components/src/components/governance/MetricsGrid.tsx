import React from "react";
import { Activity, Shield, UserCheck, Zap } from "lucide-react";

export type SystemTelemetry = {
  drift_detection_count: number;
  last_latency_ms: number;
};

export type SystemStatusSummary = {
  active_alert_level: "NONE" | "HIGH" | "CRITICAL" | string;
  waiting_for_human: boolean;
  telemetry: SystemTelemetry;
};

export interface MetricsGridProps {
  status: SystemStatusSummary | null;
}

const alertClasses = (level: string) => {
  if (level === "CRITICAL") return "text-red-400 bg-red-500/10 border-red-500/30";
  if (level === "HIGH") return "text-amber-400 bg-amber-500/10 border-amber-500/30";
  return "text-emerald-400 bg-emerald-500/10 border-emerald-500/30";
};

export const MetricsGrid: React.FC<MetricsGridProps> = ({ status }) => {
  if (!status) {
    return (
      <div className="animate-pulse flex gap-4">
        <div className="h-32 bg-white/5 rounded-xl w-full" />
      </div>
    );
  }

  const alertStyle = alertClasses(status.active_alert_level).split(" ");

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div className={`glass-panel p-4 flex flex-col justify-between border ${alertStyle[2] || ""}`}>
        <div className="flex justify-between items-start">
          <span className="text-white/50 text-sm font-medium">Sentinel Status</span>
          <Shield className={alertStyle[0]} size={20} />
        </div>
        <div className="mt-4">
          <div className={`text-2xl font-bold ${alertStyle[0]}`}>{status.active_alert_level}</div>
          <div className="text-xs text-white/30 mt-1">Real-time threat monitoring</div>
        </div>
      </div>

      <div className="glass-panel p-4 flex flex-col justify-between">
        <div className="flex justify-between items-start">
          <span className="text-white/50 text-sm font-medium">Policy Drift</span>
          <Activity className="text-blue-400" size={20} />
        </div>
        <div className="mt-4">
          <div className="text-2xl font-bold text-white">{status.telemetry.drift_detection_count}</div>
          <div className="text-xs text-white/30 mt-1">Drift events detected</div>
        </div>
      </div>

      <div className="glass-panel p-4 flex flex-col justify-between">
        <div className="flex justify-between items-start">
          <span className="text-white/50 text-sm font-medium">Core Latency</span>
          <Zap className="text-yellow-400" size={20} />
        </div>
        <div className="mt-4">
          <div className="text-2xl font-bold text-white">{status.telemetry.last_latency_ms} ms</div>
          <div className="text-xs text-white/30 mt-1">Last inference cycle</div>
        </div>
      </div>

      <div className="glass-panel p-4 flex flex-col justify-between">
        <div className="flex justify-between items-start">
          <span className="text-white/50 text-sm font-medium">Pending Review</span>
          <UserCheck className={status.waiting_for_human ? "text-purple-400" : "text-white/20"} size={20} />
        </div>
        <div className="mt-4">
          <div className="text-2xl font-bold text-white">{status.waiting_for_human ? "1" : "0"}</div>
          <div className="text-xs text-white/30 mt-1">Decisions awaiting signature</div>
        </div>
      </div>
    </div>
  );
};
