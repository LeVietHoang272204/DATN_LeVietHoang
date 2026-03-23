"use client";

import { useEffect, useState } from "react";
import AppLayout from "@/components/AppLayout";
import { useAuth } from "@/lib/auth";
import api from "@/lib/api";
import { FileText, MessageSquare, Trophy, Upload } from "lucide-react";

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    documents: 0,
    sessions: 0,
    totalScore: 0,
    mediaFiles: 0,
  });

  useEffect(() => {
    async function loadStats() {
      try {
        const [docs, sessions, media] = await Promise.all([
          api.get("/documents/"),
          api.get("/chat/sessions"),
          api.get("/media/"),
        ]);
        setStats({
          documents: docs.data.length,
          sessions: sessions.data.length,
          totalScore: user?.total_score || 0,
          mediaFiles: media.data.length,
        });
      } catch {}
    }
    loadStats();
  }, [user]);

  const cards = [
    {
      title: "Tài liệu",
      value: stats.documents,
      icon: FileText,
      color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
    },
    {
      title: "Cuộc hội thoại",
      value: stats.sessions,
      icon: MessageSquare,
      color:
        "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
    },
    {
      title: "Tổng điểm",
      value: stats.totalScore,
      icon: Trophy,
      color:
        "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
    },
    {
      title: "File cá nhân",
      value: stats.mediaFiles,
      icon: Upload,
      color:
        "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
    },
  ];

  return (
    <AppLayout>
      <div className="max-w-6xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
          Xin chào, {user?.full_name || "bạn"}! 👋
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mb-8">
          Trợ lý pháp lý AI - Phân tích và tóm tắt văn bản pháp lý
        </p>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
          {cards.map((card) => {
            const Icon = card.icon;
            return (
              <div
                key={card.title}
                className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-5"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {card.title}
                    </p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                      {card.value}
                    </p>
                  </div>
                  <div className={`p-3 rounded-lg ${card.color}`}>
                    <Icon className="w-6 h-6" />
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Quick Actions */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Bắt đầu nhanh
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <a
              href="/chat"
              className="p-4 rounded-lg border border-gray-200 dark:border-gray-600 hover:border-primary-500 dark:hover:border-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition group"
            >
              <MessageSquare className="w-8 h-8 text-primary-600 mb-2" />
              <h3 className="font-medium text-gray-900 dark:text-white">
                Tư vấn pháp lý
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Đặt câu hỏi về luật Đất đai, Lao động, Dân sự
              </p>
            </a>
            <a
              href="/library"
              className="p-4 rounded-lg border border-gray-200 dark:border-gray-600 hover:border-primary-500 dark:hover:border-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition group"
            >
              <Upload className="w-8 h-8 text-primary-600 mb-2" />
              <h3 className="font-medium text-gray-900 dark:text-white">
                Upload tài liệu
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Tải lên PDF/DOCX để phân tích và tóm tắt
              </p>
            </a>
            <a
              href="/templates"
              className="p-4 rounded-lg border border-gray-200 dark:border-gray-600 hover:border-primary-500 dark:hover:border-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition group"
            >
              <FileText className="w-8 h-8 text-primary-600 mb-2" />
              <h3 className="font-medium text-gray-900 dark:text-white">
                Soạn văn bản
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Sử dụng template hợp đồng, đơn từ, biên bản
              </p>
            </a>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
