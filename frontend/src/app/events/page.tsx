"use client";

import { useEffect, useState } from "react";
import AppLayout from "@/components/AppLayout";
import api from "@/lib/api";
import type { Event as IEvent, EventQuestion } from "@/types";
import { Trophy, Clock, CheckCircle } from "lucide-react";
import toast from "react-hot-toast";

export default function EventsPage() {
  const [events, setEvents] = useState<IEvent[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<IEvent | null>(null);
  const [questions, setQuestions] = useState<EventQuestion[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [scores, setScores] = useState<any[]>([]);
  const [totalScore, setTotalScore] = useState(0);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    loadEvents();
    loadScores();
  }, []);

  async function loadEvents() {
    try {
      const res = await api.get("/events/");
      setEvents(res.data);
    } catch {}
  }

  async function loadScores() {
    try {
      const res = await api.get("/events/scores/me");
      setScores(res.data.scores);
      setTotalScore(res.data.total_accumulated);
    } catch {}
  }

  async function loadQuestions(eventId: number) {
    try {
      const res = await api.get(`/events/${eventId}/questions`);
      setQuestions(res.data);
      setAnswers({});
      setSubmitted(false);
    } catch {}
  }

  async function handleSubmit() {
    if (!selectedEvent) return;
    try {
      const res = await api.post(`/events/${selectedEvent.id}/submit`, {
        answers,
      });
      toast.success(
        `Hoàn thành! Điểm: ${res.data.score} (${res.data.correct_answers}/${res.data.total_questions} đúng)`
      );
      setSubmitted(true);
      loadScores();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Gửi bài thất bại");
    }
  }

  return (
    <AppLayout>
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Sự kiện & Điểm
            </h1>
            <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">
              Tham gia quiz pháp lý để tích lũy điểm
            </p>
          </div>
          <div className="flex items-center gap-2 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 px-4 py-2 rounded-lg">
            <Trophy className="w-5 h-5" />
            <span className="font-bold text-lg">{totalScore}</span>
            <span className="text-sm">điểm</span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Events List */}
          <div className="lg:col-span-1 space-y-3">
            <h2 className="font-semibold text-gray-900 dark:text-white">
              Sự kiện
            </h2>
            {events.map((event) => (
              <div
                key={event.id}
                onClick={() => {
                  setSelectedEvent(event);
                  loadQuestions(event.id);
                }}
                className={`p-4 rounded-xl border cursor-pointer transition ${
                  selectedEvent?.id === event.id
                    ? "border-primary-500 bg-primary-50 dark:bg-primary-900/20"
                    : "border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-primary-300"
                }`}
              >
                <h3 className="font-medium text-gray-900 dark:text-white">
                  {event.title}
                </h3>
                {event.description && (
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    {event.description}
                  </p>
                )}
                <div className="flex items-center gap-3 mt-2 text-xs text-gray-400">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {new Date(event.end_time).toLocaleDateString("vi-VN")}
                  </span>
                  <span>{event.question_count} câu hỏi</span>
                </div>
              </div>
            ))}
            {events.length === 0 && (
              <p className="text-sm text-gray-400 py-8 text-center">
                Chưa có sự kiện nào
              </p>
            )}

            {/* Score History */}
            {scores.length > 0 && (
              <div className="mt-6">
                <h2 className="font-semibold text-gray-900 dark:text-white mb-3">
                  Lịch sử điểm
                </h2>
                <div className="space-y-2">
                  {scores.map((s) => (
                    <div
                      key={s.id}
                      className="flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
                    >
                      <div>
                        <p className="text-sm text-gray-900 dark:text-white">
                          {s.correct_answers}/{s.total_questions} đúng
                        </p>
                        <p className="text-xs text-gray-400">
                          {new Date(s.completed_at).toLocaleDateString("vi-VN")}
                        </p>
                      </div>
                      <span className="font-bold text-primary-600 dark:text-primary-400">
                        +{s.score}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Quiz Area */}
          <div className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
            {!selectedEvent ? (
              <div className="text-center py-16 text-gray-400">
                <Trophy className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>Chọn một sự kiện để bắt đầu</p>
              </div>
            ) : questions.length === 0 ? (
              <p className="text-center py-16 text-gray-400">
                Sự kiện chưa có câu hỏi
              </p>
            ) : (
              <div className="space-y-6">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  {selectedEvent.title}
                </h2>
                {questions.map((q, idx) => (
                  <div key={q.id} className="space-y-2">
                    <p className="font-medium text-gray-900 dark:text-white">
                      Câu {idx + 1}: {q.question_text}
                    </p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {q.options.map((opt, i) => (
                        <button
                          key={i}
                          onClick={() =>
                            !submitted &&
                            setAnswers((prev) => ({
                              ...prev,
                              [q.id.toString()]: opt,
                            }))
                          }
                          disabled={submitted}
                          className={`text-left px-4 py-2.5 rounded-lg border transition text-sm ${
                            answers[q.id.toString()] === opt
                              ? "border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-400"
                              : "border-gray-200 dark:border-gray-600 hover:border-primary-300"
                          } ${submitted ? "opacity-60 cursor-not-allowed" : ""}`}
                        >
                          {opt}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}

                {!submitted && (
                  <button
                    onClick={handleSubmit}
                    disabled={
                      Object.keys(answers).length !== questions.length
                    }
                    className="w-full py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition disabled:opacity-50"
                  >
                    Nộp bài ({Object.keys(answers).length}/{questions.length})
                  </button>
                )}

                {submitted && (
                  <div className="flex items-center gap-2 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg text-green-700 dark:text-green-400">
                    <CheckCircle className="w-5 h-5" />
                    Bạn đã hoàn thành bài quiz này!
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
