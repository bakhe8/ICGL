import React from "react";
import { AnimatePresence, motion } from "framer-motion";
import { CheckCircle2, Circle, Clock, Loader2, Target } from "lucide-react";

export type TaskStatus = "pending" | "in-progress" | "completed" | "failed";

export interface Task {
  id: string;
  text: string;
  status: TaskStatus;
}

export interface TaskTrackerProps {
  objective: string;
  tasks: Task[];
}

export const TaskTracker: React.FC<TaskTrackerProps> = ({ objective, tasks }) => {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="glass-card p-5 rounded-[2rem] border-indigo-500/20 bg-indigo-500/5 relative overflow-hidden"
    >
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2.5 rounded-xl bg-indigo-500/20 text-indigo-400">
          <Target className="w-5 h-5" />
        </div>
        <div>
          <span className="text-[10px] font-black text-indigo-400 uppercase tracking-widest block mb-0.5">Current Objective</span>
          <h3 className="text-sm font-bold text-white line-clamp-1">{objective || "Autonomous Evolution"}</h3>
        </div>
      </div>

      <div className="space-y-3">
        <AnimatePresence mode="popLayout">
          {tasks.map((task, idx) => (
            <motion.div
              key={task.id || idx}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className={`flex items-start gap-3 p-3 rounded-2xl border transition-all ${
                task.status === "in-progress" ? "bg-indigo-500/10 border-indigo-500/30" : "bg-white/5 border-white/5"
              }`}
            >
              <div className="mt-0.5">
                {task.status === "completed" && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                {task.status === "pending" && <Circle className="w-4 h-4 text-white/20" />}
                {task.status === "in-progress" && <Loader2 className="w-4 h-4 text-indigo-400 animate-spin" />}
                {task.status === "failed" && <Clock className="w-4 h-4 text-red-400" />}
              </div>
              <span
                className={`text-xs font-medium leading-tight ${
                  task.status === "completed" ? "text-white/40 line-through" : "text-white/80"
                }`}
              >
                {task.text}
              </span>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      <div className="mt-6 pt-4 border-t border-white/5 flex items-center justify-between">
        <div className="flex gap-1">
          {tasks.map((t, i) => (
            <div
              key={i}
              className={`h-1 w-4 rounded-full ${
                t.status === "completed" ? "bg-emerald-500" : t.status === "in-progress" ? "bg-indigo-500" : "bg-white/10"
              }`}
            />
          ))}
        </div>
        <span className="text-[10px] font-bold text-white/30 uppercase tracking-tighter">
          {tasks.filter((t) => t.status === "completed").length} / {tasks.length} Completed
        </span>
      </div>
    </motion.div>
  );
};
