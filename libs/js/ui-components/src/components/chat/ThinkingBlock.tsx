import React from "react";

export const ThinkingBlock: React.FC = () => (
  <div className="flex gap-4 p-2 items-center text-white/40 text-xs animate-pulse">
    <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center">
      <div className="flex gap-1">
        <span className="w-1 h-1 bg-white/40 rounded-full animate-bounce" style={{ animationDelay: "0s" }}></span>
        <span className="w-1 h-1 bg-white/40 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></span>
        <span className="w-1 h-1 bg-white/40 rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></span>
      </div>
    </div>
    <span>Core Reasoning Active...</span>
  </div>
);

export default ThinkingBlock;
