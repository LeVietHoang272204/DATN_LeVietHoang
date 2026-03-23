"use client";

import { useEffect, useState } from "react";
import AppLayout from "@/components/AppLayout";
import api from "@/lib/api";
import type { MediaFile } from "@/types";
import {
  Upload,
  Trash2,
  FileText,
  CheckCircle,
  Loader2,
  Edit2,
} from "lucide-react";
import toast from "react-hot-toast";

export default function LibraryPage() {
  const [files, setFiles] = useState<MediaFile[]>([]);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadFiles();
  }, []);

  async function loadFiles() {
    try {
      const res = await api.get("/media/");
      setFiles(res.data);
    } catch {}
  }

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      await api.post("/media/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      toast.success("Upload thành công!");
      loadFiles();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Upload thất bại");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  async function handleDelete(id: number) {
    if (!confirm("Bạn có chắc muốn xóa file này?")) return;
    try {
      await api.delete(`/media/${id}`);
      setFiles((prev) => prev.filter((f) => f.id !== id));
      toast.success("Đã xóa file");
    } catch {}
  }

  async function handleRename(id: number) {
    const newName = prompt("Nhập tên mới:");
    if (!newName) return;
    try {
      await api.put(`/media/${id}/rename`, { new_filename: newName });
      loadFiles();
    } catch {}
  }

  return (
    <AppLayout>
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Thư viện tài liệu
            </h1>
            <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">
              Upload tài liệu cá nhân để hỏi đáp trực tiếp (Personal RAG)
            </p>
          </div>
          <label className="flex items-center gap-2 px-4 py-2.5 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition cursor-pointer">
            {uploading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Upload className="w-4 h-4" />
            )}
            {uploading ? "Đang upload..." : "Upload file"}
            <input
              type="file"
              accept=".pdf,.docx,.png,.jpg,.jpeg"
              onChange={handleUpload}
              className="hidden"
              disabled={uploading}
            />
          </label>
        </div>

        {files.length === 0 ? (
          <div className="text-center py-20 text-gray-400 dark:text-gray-500">
            <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
            <p>Chưa có tài liệu nào. Upload file để bắt đầu!</p>
          </div>
        ) : (
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-700/50">
                <tr>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Tên file
                  </th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Loại
                  </th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Kích thước
                  </th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Trạng thái
                  </th>
                  <th className="text-right px-4 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Hành động
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {files.map((f) => (
                  <tr
                    key={f.id}
                    className="hover:bg-gray-50 dark:hover:bg-gray-700/30 transition"
                  >
                    <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">
                      {f.original_filename}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500 dark:text-gray-400 uppercase">
                      {f.file_type}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500 dark:text-gray-400">
                      {(f.file_size / 1024).toFixed(1)} KB
                    </td>
                    <td className="px-4 py-3">
                      {f.is_indexed ? (
                        <span className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">
                          <CheckCircle className="w-3 h-3" />
                          Đã index
                        </span>
                      ) : f.processing_status === "processing" ? (
                        <span className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400">
                          <Loader2 className="w-3 h-3 animate-spin" />
                          Đang xử lý
                        </span>
                      ) : (
                        <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400">
                          {f.processing_status}
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleRename(f.id)}
                          className="p-1.5 text-gray-400 hover:text-primary-600 transition"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(f.id)}
                          className="p-1.5 text-gray-400 hover:text-red-600 transition"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
