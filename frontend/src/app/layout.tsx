import type { Metadata } from "next";
import "./globals.css";
import { Toaster } from "react-hot-toast";

export const metadata: Metadata = {
  title: "Legal AI Assistant - Trợ lý Pháp lý AI",
  description:
    "Hệ thống phân tích và tóm tắt văn bản pháp lý ứng dụng Multimodal RAG với LLM",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi">
      <body className="antialiased">
        {children}
        <Toaster position="top-right" />
      </body>
    </html>
  );
}
