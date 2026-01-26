import React, { useEffect, useRef } from "react";
import mermaid from "mermaid";

mermaid.initialize({
  startOnLoad: true,
  theme: "dark",
  securityLevel: "loose",
  fontFamily: "Space Grotesk, sans-serif",
});

export interface MermaidProps {
  chart: string;
}

export const Mermaid: React.FC<MermaidProps> = ({ chart }) => {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (ref.current && chart) {
      mermaid.contentLoaded();
      mermaid.render("mermaid-chart-" + Math.random().toString(36).substr(2, 9), chart).then((result) => {
        if (ref.current) {
          ref.current.innerHTML = result.svg;
        }
      });
    }
  }, [chart]);

  return <div key={chart} ref={ref} className="mermaid-chart flex justify-center bg-black/20 p-4 rounded-xl border border-white/5 my-4" />;
};
