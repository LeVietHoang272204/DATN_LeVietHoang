"use client";

import { useEffect, useState } from "react";
import AppLayout from "@/components/AppLayout";
import api from "@/lib/api";
import type { Template } from "@/types";
import { FileEdit, Download } from "lucide-react";
import toast from "react-hot-toast";

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selected, setSelected] = useState<Template | null>(null);
  const [fieldValues, setFieldValues] = useState<Record<string, string>>({});
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    loadTemplates();
  }, []);

  async function loadTemplates() {
    try {
      const res = await api.get("/templates/");
      setTemplates(res.data);
    } catch {}
  }

  function selectTemplate(tpl: Template) {
    setSelected(tpl);
    const values: Record<string, string> = {};
    tpl.fields.forEach((f) => {
      values[f.name] = "";
    });
    setFieldValues(values);
  }

  async function handleGenerate() {
    if (!selected) return;
    setGenerating(true);
    try {
      const response = await api.post(
        "/templates/generate",
        {
          template_id: selected.id,
          field_values: fieldValues,
          output_format: "docx",
        },
        { responseType: "blob" }
      );

      // Download file
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `${selected.name}.docx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success("Đã tạo văn bản!");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Tạo văn bản thất bại");
    } finally {
      setGenerating(false);
    }
  }

  const categories = [...new Set(templates.map((t) => t.category))];

  return (
    <AppLayout>
      <div className="max-w-5xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
          Template văn bản
        </h1>
        <p className="text-gray-500 dark:text-gray-400 text-sm mb-6">
          Soạn thảo hợp đồng, đơn từ, biên bản nhanh chóng
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Template List */}
          <div className="lg:col-span-1 space-y-4">
            {categories.map((cat) => (
              <div key={cat}>
                <h3 className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">
                  {cat}
                </h3>
                <div className="space-y-1">
                  {templates
                    .filter((t) => t.category === cat)
                    .map((tpl) => (
                      <button
                        key={tpl.id}
                        onClick={() => selectTemplate(tpl)}
                        className={`w-full text-left px-3 py-2.5 rounded-lg text-sm transition ${
                          selected?.id === tpl.id
                            ? "bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400"
                            : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700/50"
                        }`}
                      >
                        <span className="font-medium">{tpl.name}</span>
                        {tpl.description && (
                          <p className="text-xs text-gray-400 mt-0.5">
                            {tpl.description}
                          </p>
                        )}
                      </button>
                    ))}
                </div>
              </div>
            ))}
            {templates.length === 0 && (
              <p className="text-center text-gray-400 py-8 text-sm">
                Chưa có template nào
              </p>
            )}
          </div>

          {/* Form */}
          <div className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
            {!selected ? (
              <div className="text-center py-16 text-gray-400">
                <FileEdit className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>Chọn một template để bắt đầu soạn thảo</p>
              </div>
            ) : (
              <div className="space-y-5">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  {selected.name}
                </h2>
                {selected.description && (
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {selected.description}
                  </p>
                )}

                <div className="space-y-4">
                  {selected.fields.map((field) => (
                    <div key={field.name}>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        {field.label}
                        {field.required && (
                          <span className="text-red-500 ml-1">*</span>
                        )}
                      </label>
                      {field.type === "textarea" ? (
                        <textarea
                          value={fieldValues[field.name] || ""}
                          onChange={(e) =>
                            setFieldValues((prev) => ({
                              ...prev,
                              [field.name]: e.target.value,
                            }))
                          }
                          rows={3}
                          className="w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 outline-none transition"
                        />
                      ) : (
                        <input
                          type={field.type === "date" ? "date" : "text"}
                          value={fieldValues[field.name] || ""}
                          onChange={(e) =>
                            setFieldValues((prev) => ({
                              ...prev,
                              [field.name]: e.target.value,
                            }))
                          }
                          className="w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 outline-none transition"
                        />
                      )}
                    </div>
                  ))}
                </div>

                <button
                  onClick={handleGenerate}
                  disabled={generating}
                  className="flex items-center justify-center gap-2 w-full py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition disabled:opacity-50"
                >
                  <Download className="w-5 h-5" />
                  {generating ? "Đang tạo..." : "Tạo & Tải xuống DOCX"}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
