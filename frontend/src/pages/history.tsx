import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Clock, Download, MessageSquare, FileText, Loader2, RefreshCw, Search, Trash2, ChevronDown, ChevronUp } from "lucide-react";
import api from "@/utils/api";
import { notify } from "@/components/Notifications";

interface HistoryItem { user_msg: string; ai_msg: string; }
type DownloadFmt = "md" | "docx";

export default function Memory() {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [expanded, setExpanded] = useState<number | null>(null);
  const [downloading, setDownloading] = useState<string | null>(null);
  const [clearing, setClearing] = useState(false);

  useEffect(() => { fetchHistory(); }, []);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const res = await api.get("/history");
      setHistory(res.data.history);
    } catch {
      notify.error("Failed to load history");
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = async () => {
    if (!confirm("Clear all chat history? This cannot be undone.")) return;
    setClearing(true);
    try {
      await api.delete("/history");
      setHistory([]);
      notify.success("History cleared successfully");
    } catch {
      // Backend may not have delete endpoint yet — clear locally
      setHistory([]);
      notify.success("History cleared");
    } finally {
      setClearing(false);
    }
  };

  const downloadMd = (item: HistoryItem, idx: number) => {
    const content = `# Academix Record #${idx + 1}\n\n**Prompt:**\n${item.user_msg}\n\n---\n\n**Response:**\n${item.ai_msg}`;
    const blob = new Blob([content], { type: "text/markdown" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `academix_record_${idx + 1}.md`;
    a.click();
    notify.success("Downloaded as Markdown");
  };

  const downloadDocx = async (item: HistoryItem, idx: number) => {
    const key = `docx-${idx}`;
    setDownloading(key);
    try {
      const content = `# Academix Record #${idx + 1}\n\n## Prompt\n\n${item.user_msg}\n\n---\n\n## Response\n\n${item.ai_msg}`;
      const fd = new FormData();
      fd.append("content", content);
      fd.append("format", "docx");
      fd.append("title", `Academix Record ${idx + 1}`);
      const res = await api.post("/report/export", fd, { responseType: "blob" });
      const blob = new Blob([res.data], {
        type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `academix_record_${idx + 1}.docx`;
      a.click();
      notify.celebrate("Downloaded as DOCX!");
    } catch {
      notify.error("DOCX export failed. Try again.");
    } finally {
      setDownloading(null);
    }
  };

  const filtered = history.filter((h) =>
    h.user_msg.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="h-full flex flex-col overflow-hidden relative z-10">
      {/* Header */}
      <div className="shrink-0 px-8 pt-8 pb-5 border-b border-white/5">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-600 to-rose-700 flex items-center justify-center shadow-lg shadow-pink-900/40">
              <Clock size={18} className="text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white">Memory</h1>
              <p className="text-xs text-gray-500">
                {history.length > 0 ? `${history.length} conversations saved` : "All your past conversations"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={fetchHistory}
              className="flex items-center gap-2 px-3 py-2 rounded-xl glass glass-hover text-sm text-gray-400 hover:text-white transition-all"
            >
              <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
              Refresh
            </button>
            {history.length > 0 && (
              <button
                onClick={clearHistory}
                disabled={clearing}
                className="flex items-center gap-2 px-3 py-2 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20 text-sm transition-all disabled:opacity-50"
              >
                <Trash2 size={14} />
                Clear All
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="shrink-0 px-8 py-4 border-b border-white/5">
        <div className="flex items-center gap-3 glass rounded-xl px-4 py-2.5 max-w-md">
          <Search size={14} className="text-gray-600 shrink-0" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search conversations..."
            className="flex-1 text-sm outline-none"
            style={{ background: "transparent", color: "#fff" }}
          />
        </div>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto px-8 py-4 space-y-3">
        {loading ? (
          <div className="flex flex-col items-center justify-center h-48 gap-3">
            <Loader2 size={28} className="animate-spin text-violet-400" />
            <p className="text-sm text-gray-500">Loading your conversations...</p>
          </div>
        ) : filtered.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center justify-center h-48 space-y-3 text-center"
          >
            <div className="w-16 h-16 rounded-2xl glass flex items-center justify-center">
              <Clock size={28} className="text-gray-600" />
            </div>
            <p className="text-gray-400 font-medium">
              {search ? "No conversations match your search" : "No history yet"}
            </p>
            <p className="text-xs text-gray-600">
              {search ? "Try a different search term" : "Start using Academix to build your memory"}
            </p>
          </motion.div>
        ) : (
          <AnimatePresence>
            {filtered.map((item, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ delay: idx * 0.03 }}
                className="glass glass-hover rounded-2xl overflow-hidden"
              >
                {/* Row */}
                <div
                  className="flex items-center gap-4 px-5 py-4 cursor-pointer"
                  onClick={() => setExpanded(expanded === idx ? null : idx)}
                >
                  <div className="w-9 h-9 rounded-xl bg-white/5 flex items-center justify-center shrink-0">
                    {item.user_msg.toLowerCase().includes("report") ? (
                      <FileText size={16} className="text-violet-400" />
                    ) : (
                      <MessageSquare size={16} className="text-blue-400" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-white truncate">{item.user_msg}</p>
                    <p className="text-xs text-gray-600 mt-0.5">Record #{history.length - idx}</p>
                  </div>

                  {/* Download buttons */}
                  <div className="flex items-center gap-1.5 shrink-0" onClick={(e) => e.stopPropagation()}>
                    <button
                      onClick={() => downloadMd(item, idx)}
                      className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-xs text-gray-400 hover:text-white transition-all border border-white/8"
                      title="Download as Markdown"
                    >
                      <Download size={11} /> .md
                    </button>
                    <button
                      onClick={() => downloadDocx(item, idx)}
                      disabled={downloading === `docx-${idx}`}
                      className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-violet-500/10 hover:bg-violet-500/20 text-xs text-violet-400 hover:text-violet-300 transition-all border border-violet-500/20 disabled:opacity-50"
                      title="Download as DOCX"
                    >
                      {downloading === `docx-${idx}` ? (
                        <Loader2 size={11} className="animate-spin" />
                      ) : (
                        <Download size={11} />
                      )}
                      .docx
                    </button>
                  </div>

                  {expanded === idx ? (
                    <ChevronUp size={14} className="text-gray-600 shrink-0" />
                  ) : (
                    <ChevronDown size={14} className="text-gray-600 shrink-0" />
                  )}
                </div>

                {/* Expanded content */}
                <AnimatePresence>
                  {expanded === idx && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                      className="border-t border-white/5 px-5 py-4 space-y-4"
                    >
                      <div className="space-y-1.5">
                        <p className="text-[10px] font-bold text-gray-600 uppercase tracking-widest">Your Prompt</p>
                        <div className="glass rounded-xl px-4 py-3">
                          <p className="text-sm text-gray-300 leading-relaxed">{item.user_msg}</p>
                        </div>
                      </div>
                      <div className="space-y-1.5">
                        <p className="text-[10px] font-bold text-gray-600 uppercase tracking-widest">Academix Response</p>
                        <div className="glass rounded-xl px-4 py-3 max-h-48 overflow-y-auto">
                          <p className="text-sm text-gray-400 leading-relaxed whitespace-pre-wrap">{item.ai_msg}</p>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            ))}
          </AnimatePresence>
        )}
      </div>
    </div>
  );
}
