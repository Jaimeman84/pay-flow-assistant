"use client";

import { FormEvent, useRef } from "react";

const SUGGESTIONS = [
  "What open Jira bugs are blocking the payment release?",
  "What does Confluence say about the payment confirmation flow?",
  "Which Figma screen includes the freeze card toggle?",
  "What changed in the login flow and is there a related Jira bug?",
  "What is PayFlow and what does it do?",
  "What is the weather in London today?",
];

interface Props {
  onSubmit: (message: string) => void;
  loading: boolean;
}

export function ChatInput({ onSubmit, loading }: Props) {
  const ref = useRef<HTMLTextAreaElement>(null);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const value = ref.current?.value.trim();
    if (!value || loading) return;
    onSubmit(value);
    if (ref.current) ref.current.value = "";
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as FormEvent);
    }
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => {
              if (ref.current) ref.current.value = s;
              ref.current?.focus();
            }}
            className="rounded-full border border-gray-200 bg-white px-3 py-1 text-xs text-gray-600 hover:bg-gray-50 hover:border-gray-300 transition-colors text-left"
          >
            {s.length > 50 ? s.slice(0, 48) + "…" : s}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2 items-end">
        <textarea
          ref={ref}
          rows={2}
          onKeyDown={handleKeyDown}
          placeholder="Ask something about PayFlow…"
          className="flex-1 resize-none rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-indigo-300 transition-all"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading}
          className="shrink-0 rounded-xl bg-indigo-600 px-5 py-3 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <span className="flex items-center gap-1.5">
              <span className="h-3.5 w-3.5 rounded-full border-2 border-white border-t-transparent animate-spin" />
              Thinking
            </span>
          ) : (
            "Send"
          )}
        </button>
      </form>
    </div>
  );
}
