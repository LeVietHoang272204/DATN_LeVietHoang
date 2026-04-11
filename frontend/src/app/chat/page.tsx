"use client";

import { useEffect, useState, useRef } from "react";
import AppLayout from "@/components/AppLayout";
import api from "@/lib/api";
import type { ChatSession, ChatMessage, SourceReference } from "@/types";
import { Send, Plus, Trash2, AlertTriangle, BookOpen } from "lucide-react";
import ReactMarkdown from "react-markdown";
import toast from "react-hot-toast";

export default function ChatPage() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<number | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [usePersonalDocs, setUsePersonalDocs] = useState(false);
  const [sources, setSources] = useState<SourceReference[]>([]);
  const [warning, setWarning] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function loadSessions() {
    try {
      const res = await api.get("/chat/sessions");
      setSessions(res.data);
    } catch {}
  }

  async function loadSession(sessionId: number) {
    try {
      const res = await api.get(`/chat/sessions/${sessionId}`);
      setActiveSessionId(sessionId);
      setMessages(res.data.messages);
      setSources([]);
      setWarning(null);
    } catch {}
  }

  function newChat() {
    setActiveSessionId(null);
    setMessages([]);
    setSources([]);
    setWarning(null);
  }

  async function sendMessage() {
    if (!input.trim() || sending) return;
    const content = input.trim();
    setInput("");
    setSending(true);
    setWarning(null);

    // Optimistic UI
    const userMsg: ChatMessage = {
      id: Date.now(),
      role: "user",
      content,
      confidence_score: null,
      sources: null,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const res = await api.post("/chat/send", {
        content,
        session_id: activeSessionId,
        use_personal_docs: usePersonalDocs,
      });

      setActiveSessionId(res.data.session_id);
      setMessages((prev) => [...prev, res.data.message]);
      setSources(res.data.sources || []);
      setWarning(res.data.warning || null);
      loadSessions();
    } catch (err: any) {
      toast.error("Gửi tin nhắn thất bại");
      setMessages((prev) => prev.filter((m) => m.id !== userMsg.id));
    } finally {
      setSending(false);
    }
  }

  async function deleteSession(sessionId: number) {
    try {
      await api.delete(`/chat/sessions/${sessionId}`);
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
      if (activeSessionId === sessionId) newChat();
    } catch {}
  }

  return (
    <AppLayout>
      <div className="flex h-[calc(100vh-3rem)] gap-4">
        {/* Sidebar - Sessions */}
        <div className="w-72 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 flex flex-col">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <button
              onClick={newChat}
              className="w-full flex items-center justify-center gap-2 py-2.5 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition"
            >
              <Plus className="w-4 h-4" />
              Cuộc trò chuyện mới
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {sessions.map((s) => (
              <div
                key={s.id}
                className={`group flex items-center justify-between px-3 py-2.5 rounded-lg cursor-pointer transition ${
                  activeSessionId === s.id
                    ? "bg-primary-50 dark:bg-primary-900/30"
                    : "hover:bg-gray-100 dark:hover:bg-gray-700/50"
                }`}
                onClick={() => loadSession(s.id)}
              >
                <span className="text-sm truncate text-gray-900 dark:text-white flex-1">
                  {s.title}
                </span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteSession(s.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-700 transition"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-gray-400 dark:text-gray-500 mt-20">
                <BookOpen className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p className="text-lg">Đặt câu hỏi pháp lý của bạn</p>
                <p className="text-sm mt-1">
                  Hỗ trợ: Đất đai, Lao động, Dân sự
                </p>
              </div>
            )}
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[75%] px-4 py-3 rounded-2xl ${
                    msg.role === "user"
                      ? "bg-primary-600 text-white"
                      : "bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white"
                  }`}
                >
                  {msg.role === "assistant" ? (
                    <div className="prose prose-sm dark:prose-invert max-w-none">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                      {msg.confidence_score !== null && (
                        <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                          Độ tin cậy: {(msg.confidence_score * 100).toFixed(0)}%
                        </div>
                      )}
                    </div>
                  ) : (
                    <p>{msg.content}</p>
                  )}
                </div>
              </div>
            ))}

            {/* Warning */}
            {warning && (
              <div className="flex items-center gap-2 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg text-sm text-yellow-700 dark:text-yellow-400">
                <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                {warning}
              </div>
            )}

            {sending && (
              <div className="flex justify-start">
                <div className="bg-gray-100 dark:bg-gray-700 rounded-2xl px-4 py-3">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" />
                    <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce [animation-delay:0.1s]" />
                    <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce [animation-delay:0.2s]" />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex gap-2">
              <input
                id="chat-input"
                name="chat-input"
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
                placeholder="Nhập câu hỏi pháp lý..."
                className="flex-1 px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 outline-none transition"
                disabled={sending}
              />
              <button
                onClick={sendMessage}
                disabled={!input.trim() || sending}
                className="px-4 py-2.5 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition disabled:opacity-50"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Sources Panel */}
        {sources.length > 0 && (
          <div className="w-72 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 overflow-y-auto">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-3">
              Nguồn trích dẫn
            </h3>
            <div className="space-y-3">
              {sources.map((src, i) => (
                <div
                  key={i}
                  className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg"
                >
                  <p className="text-xs font-medium text-primary-600 dark:text-primary-400">
                    {src.document_title}
                  </p>
                  {src.document_number && (
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {src.document_number}
                    </p>
                  )}
                  <p className="text-xs text-gray-600 dark:text-gray-300 mt-1 line-clamp-4">
                    {src.chunk_text}
                  </p>
                  <div className="mt-1 text-xs text-gray-400">
                    Độ liên quan: {(src.relevance_score * 100).toFixed(0)}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
