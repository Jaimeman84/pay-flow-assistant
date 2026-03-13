"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { ChatInput } from "@/components/ChatInput";
import { ResponseView } from "@/components/ResponseView";
import { ChatMessage, ChatResponse } from "@/types/chat";

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function handleSubmit(message: string) {
    setLoading(true);
    setError(null);

    const userMessage: ChatMessage = { role: "user", content: message };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, session_id: "ui-session", user_role: "student" }),
      });

      if (!res.ok) {
        throw new Error(`API returned ${res.status}`);
      }

      const data: ChatResponse = await res.json();
      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: data.answer,
        response: data,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="h-screen bg-gray-50 flex flex-col overflow-hidden">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white px-6 py-4">
        <div className="mx-auto max-w-7xl flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600">
              <span className="text-white text-sm font-bold">P</span>
            </div>
            <div>
              <h1 className="text-sm font-semibold text-gray-900">PayFlow GenAI Demo</h1>
              <p className="text-xs text-gray-500">Multi-agent specialist system</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-xs text-gray-500">
              <span className="h-2 w-2 rounded-full bg-green-400" />
              Jira · Confluence · Figma · Basic
            </div>
            <Link
              href="/questions"
              className="rounded-lg border border-indigo-200 bg-indigo-50 px-3 py-1.5 text-xs font-medium text-indigo-700 hover:bg-indigo-100 transition-colors"
            >
              Question guide
            </Link>
          </div>
        </div>
      </header>

      {/* Conversation */}
      <main className="flex-1 overflow-y-auto px-6 py-6">
        <div className="mx-auto max-w-7xl space-y-8">
          {messages.length === 0 && !loading && (
            <div className="flex flex-col items-center justify-center py-24 text-center">
              <div className="text-4xl mb-4">💬</div>
              <h2 className="text-lg font-semibold text-gray-700 mb-2">
                Ask anything about PayFlow
              </h2>
              <p className="text-sm text-gray-500 max-w-md">
                Questions are routed to Jira, Confluence, Figma, or Basic Knowledge specialists.
                You can see exactly how the pipeline routes and retrieves data on the right side of each response.
              </p>
            </div>
          )}

          {messages.map((msg, i) => {
            if (msg.role === "user") {
              return (
                <div key={i} className="flex justify-end">
                  <div className="rounded-2xl rounded-tr-sm bg-indigo-600 px-4 py-3 max-w-xl">
                    <p className="text-sm text-white">{msg.content}</p>
                  </div>
                </div>
              );
            }

            return (
              <div key={i} className="space-y-3">
                {msg.response && <ResponseView response={msg.response} />}
              </div>
            );
          })}

          {loading && (
            <div className="flex items-center gap-3 text-sm text-gray-500">
              <div className="flex gap-1">
                <span className="h-2 w-2 rounded-full bg-gray-400 animate-bounce [animation-delay:-0.3s]" />
                <span className="h-2 w-2 rounded-full bg-gray-400 animate-bounce [animation-delay:-0.15s]" />
                <span className="h-2 w-2 rounded-full bg-gray-400 animate-bounce" />
              </div>
              Running pipeline…
            </div>
          )}

          {error && (
            <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error} — make sure the FastAPI server is running on port 8000.
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      </main>

      {/* Input */}
      <div className="border-t border-gray-200 bg-white px-6 py-4">
        <div className="mx-auto max-w-7xl">
          <ChatInput onSubmit={handleSubmit} loading={loading} />
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-gray-100 bg-white px-6 py-2 text-center">
        <p className="text-xs text-gray-400">Made with ❤️ by Jaime Mantilla, MSIT + AI</p>
      </div>
    </div>
  );
}
