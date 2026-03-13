"use client";

import { useState } from "react";
import { DebugInfo } from "@/types/chat";

function stepIcon(step: string) {
  if (step.toLowerCase().includes("guard")) return "🛡️";
  if (step.toLowerCase().includes("orchestrator")) return "🔀";
  if (step.toLowerCase().includes("specialist")) return "🔍";
  if (step.toLowerCase().includes("synthesis") || step.toLowerCase().includes("synthesiz")) return "✍️";
  return "▸";
}

export function DebugTrace({ debug }: { debug: DebugInfo }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-gray-50 transition-colors"
      >
        <span className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          Debug Trace
          <span className="ml-2 font-mono font-normal normal-case text-gray-400">
            ({debug.steps.length} steps)
          </span>
        </span>
        <span className="text-gray-400 text-sm">{open ? "▲" : "▼"}</span>
      </button>

      {open && (
        <div className="border-t border-gray-100 px-4 py-3 space-y-3">
          {debug.app_specialist_task && (
            <div className="rounded-lg bg-indigo-50 border border-indigo-100 px-3 py-2">
              <span className="text-xs font-medium text-indigo-600">Task: </span>
              <span className="text-xs text-indigo-800">{debug.app_specialist_task}</span>
            </div>
          )}
          <ol className="space-y-1.5">
            {debug.steps.map((step, i) => (
              <li key={i} className="flex items-start gap-2 text-xs text-gray-700">
                <span className="shrink-0 text-base leading-none mt-0.5">
                  {stepIcon(step)}
                </span>
                <span className="leading-snug font-mono">{step}</span>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}
