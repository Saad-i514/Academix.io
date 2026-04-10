import React, { useRef, useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, FileText, Sparkles, Loader2, CheckCircle, X, Download, AlertCircle } from "lucide-react";
import api from "@/utils/api";
import { useReportStore } from "@/store/taskStore";
import { notify, getGoodwillMessage } from "@/components/Notifications";

type ExportFmt = "docx";

const STEPS = [
  "Scanning document...",
  "Extracting content...",
  "AI agents collaborating...",
  "Generating report structure...",
  "Finalizing output...",
];

export default function ReportStudio() {
  const {
    stage, result, error, stepIdx, fileName,
    setStage, setResult, setError, setStepIdx, setFileName, reset,
  } = useReportStore();

  // Local UI state — doesn't need to persist across navigation
  const [file, setFile] = React.useState<File | null>(null);
  const [prompt, setPrompt] = React.useState("");
  const [exporting, setExporting] = React.useState<ExportFmt | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const goodwillRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const goodwillIdx = useRef(0);

  // Resume step animation if we navigate back while processing
  useEffect(() => {
    if (stage === "processing") {
      intervalRef.current = setInterval(() => {
        setStepIdx(Math.min(useReportStore.getState().stepIdx + 1, STEPS.length - 1));
      }, 3000);
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [stage]);

  const handleGenerate = async () => {
    if (!file && !prompt.trim()) return;

    setStage("processing");
    setStepIdx(0);
    setError("");
    setFileName(file?.name || "Manual Input");

    // Thank you popup
    notify.info("🙏 Thank you! We're processing your request. Feel free to explore other features.");

    intervalRef.current = setInterval(() => {
      setStepIdx(Math.min(useReportStore.getState().stepIdx + 1, STEPS.length - 1));
    }, 3000);

    // Goodwill messages every 25 seconds
    goodwillIdx.current = 0;
    goodwillRef.current = setInterval(() => {
      notify.info(getGoodwillMessage(goodwillIdx.current++));
    }, 25000);

    const fd = new FormData();
    if (file) fd.append("file", file);
    if (prompt) fd.append("prompt", prompt);

    try {
      const res = await api.post("/report", fd);
      if (intervalRef.current) clearInterval(intervalRef.current);
      if (goodwillRef.current) clearInterval(goodwillRef.current);
      setResult(res.data.result);
      setStage("done");
      notify.celebrate("🎉 Your report is ready! Download it below.");
    } catch (e: any) {
      if (intervalRef.current) clearInterval(intervalRef.current);
      if (goodwillRef.current) clearInterval(goodwillRef.current);
      const msg = e?.response?.data?.detail || "Report generation failed. Check your API keys in Settings.";
      setError(msg);
      setStage("error");
      notify.error(msg.slice(0, 80));
    }
  };

  const handleExport = async (format: ExportFmt) => {
    setExporting(format);
    try {
      const fd = new FormData();
      fd.append("content", result);
      fd.append("format", format);
      const titleMatch = result.match(/^#\s+(.+)/m);
      fd.append("title", titleMatch ? titleMatch[1] : "Academic Report");

      const res = await api.post("/report/export", fd, { responseType: "blob" });
      const ext = format === "docx" ? "docx" : "pdf";
      const mime = format === "docx"
        ? "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        : "application/pdf";
      const blob = new Blob([res.data], { type: mime });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `academix_report_${Date.now()}.${ext}`;
      a.click();
      URL.revokeObjectURL(url);
      notify.celebrate("Downloaded as DOCX!");
    } catch {
      notify.error(`Export to ${format.toUpperCase()} failed. Please try again.`);
    } finally {
      setExporting(null);
    }
  };

  return (
    <div className="h-full flex flex-col overflow-hidden relative z-10">
      {/* Header */}
      <div className="shrink-0 px-8 pt-8 pb-5 border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-600 to-purple-700 flex items-center justify-center shadow-lg shadow-violet-900/40">
            <FileText size={18} className="text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-white">Report Studio</h1>
            <p className="text-xs text-gray-500">Upload a document or describe what you need — we'll handle the rest</p>
          </div>
          {/* Persistent status badge visible from any page */}
          {stage === "processing" && (
            <div className="ml-auto flex items-center gap-2 px-3 py-1.5 rounded-full bg-violet-500/20 border border-violet-500/30">
              <Loader2 size={12} className="animate-spin text-violet-400" />
              <span className="text-xs text-violet-300 font-medium">Processing...</span>
            </div>
          )}
          {stage === "done" && (
            <div className="ml-auto flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/20 border border-emerald-500/30">
              <CheckCircle size={12} className="text-emerald-400" />
              <span className="text-xs text-emerald-300 font-medium">Report Ready</span>
            </div>
          )}
        </div>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto">
        <AnimatePresence mode="wait">

          {/* ── INPUT ── */}
          {(stage === "idle" || stage === "error") && (
            <motion.div key="input" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="p-8 grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-6xl">
              <div className="space-y-4">
                <div className="glass rounded-2xl p-6 space-y-4">
                  <div className="flex items-center gap-2">
                    <Upload size={16} className="text-violet-400" />
                    <h3 className="font-semibold text-sm text-white">Upload Document</h3>
                    <span className="text-xs text-gray-600 ml-auto">PDF, DOCX</span>
                  </div>
                  <div
                    onClick={() => fileRef.current?.click()}
                    className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200
                      ${file ? "border-violet-500/50 bg-violet-500/5" : "border-white/10 hover:border-violet-500/30"}`}
                  >
                    <input ref={fileRef} type="file" accept=".pdf,.docx,.doc" className="hidden"
                      onChange={(e) => setFile(e.target.files?.[0] || null)} />
                    {file ? (
                      <div className="space-y-2">
                        <FileText size={32} className="mx-auto text-violet-400" />
                        <p className="text-sm font-medium text-white">{file.name}</p>
                        <p className="text-xs text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
                        <button onClick={(e) => { e.stopPropagation(); setFile(null); }}
                          className="text-xs text-red-400 hover:text-red-300 flex items-center gap-1 mx-auto">
                          <X size={12} /> Remove
                        </button>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        <Upload size={32} className="mx-auto text-gray-600" />
                        <p className="text-sm text-gray-500">Click to upload lab manual or assignment</p>
                        <p className="text-xs text-gray-700">PDF or DOCX</p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="glass rounded-2xl p-6 space-y-3">
                  <div className="flex items-center gap-2">
                    <Sparkles size={16} className="text-purple-400" />
                    <h3 className="font-semibold text-sm text-white">Instructions</h3>
                    <span className="text-xs text-gray-600 ml-auto">Optional</span>
                  </div>
                  <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)}
                    placeholder="E.g., Generate a complete lab report on Newton's Laws including theory, Octave code, and conclusion..."
                    rows={5}
                    className="w-full rounded-xl px-4 py-3 text-sm outline-none resize-none transition-colors border border-white/10 focus:border-violet-500/50"
                    style={{ background: "rgba(255,255,255,0.06)", color: "#fff" }} />
                </div>

                {stage === "error" && (
                  <div className="flex items-start gap-3 bg-red-500/10 border border-red-500/20 rounded-xl p-4">
                    <AlertCircle size={16} className="text-red-400 shrink-0 mt-0.5" />
                    <p className="text-sm text-red-300">{error}</p>
                  </div>
                )}

                <button onClick={handleGenerate} disabled={!file && !prompt.trim()}
                  className="w-full py-4 rounded-xl bg-gradient-to-r from-violet-600 to-purple-700 hover:from-violet-500 hover:to-purple-600 disabled:opacity-40 disabled:cursor-not-allowed font-bold text-sm transition-all shadow-lg shadow-violet-900/30 flex items-center justify-center gap-2">
                  <Sparkles size={16} /> Generate Report
                </button>
              </div>

              <div className="glass rounded-2xl p-6 flex flex-col items-center justify-center min-h-[400px] text-center space-y-3">
                <FileText size={48} className="text-gray-700" />
                <p className="text-gray-500 font-medium">Your report will appear here</p>
                <p className="text-xs text-gray-700 max-w-xs">Upload a document or provide instructions, then click Generate Report</p>
              </div>
            </motion.div>
          )}

          {/* ── PROCESSING ── */}
          {stage === "processing" && (
            <motion.div key="processing" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center min-h-[60vh] p-8 space-y-8">
              <div className="text-center space-y-3">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-600 to-purple-700 flex items-center justify-center mx-auto shadow-lg shadow-violet-900/40 animate-pulse">
                  <Sparkles size={28} className="text-white" />
                </div>
                <h2 className="text-xl font-bold text-white">Processing Your Request</h2>
                <p className="text-sm text-gray-500">{fileName ? `Working on: ${fileName}` : "Our AI agents are working on your report"}</p>
              </div>

              <div className="w-full max-w-md space-y-3">
                {STEPS.map((step, i) => (
                  <motion.div key={step} initial={{ opacity: 0, x: -20 }} animate={{ opacity: i <= stepIdx ? 1 : 0.3, x: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                      i < stepIdx  ? "bg-emerald-500/10 border border-emerald-500/20" :
                      i === stepIdx ? "bg-violet-500/10 border border-violet-500/20" :
                      "bg-white/5 border border-white/5"}`}>
                    {i < stepIdx  ? <CheckCircle size={16} className="text-emerald-400 shrink-0" /> :
                     i === stepIdx ? <Loader2 size={16} className="text-violet-400 animate-spin shrink-0" /> :
                     <div className="w-4 h-4 rounded-full border border-white/20 shrink-0" />}
                    <span className={`text-sm ${i <= stepIdx ? "text-white" : "text-gray-600"}`}>{step}</span>
                  </motion.div>
                ))}
              </div>

              <div className="glass rounded-xl px-6 py-4 text-center max-w-sm">
                <p className="text-sm text-gray-400">🙏 Thank you for using Academix.io</p>
                <p className="text-xs text-gray-600 mt-1">You can navigate away — we'll keep working. Come back anytime.</p>
              </div>
            </motion.div>
          )}

          {/* ── DONE ── */}
          {stage === "done" && (
            <motion.div key="done" initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              className="p-8 space-y-5 max-w-4xl">
              <div className="flex items-center justify-between flex-wrap gap-3">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center">
                    <CheckCircle size={16} className="text-emerald-400" />
                  </div>
                  <div>
                    <p className="font-semibold text-white text-sm">Report Generated Successfully</p>
                    <p className="text-xs text-gray-500">{fileName && `Source: ${fileName}`}</p>
                  </div>
                </div>
                <div className="flex gap-2 flex-wrap">
                  <button onClick={() => handleExport("docx")} disabled={!!exporting}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600/20 border border-blue-500/30 text-blue-400 hover:bg-blue-600/30 text-sm font-medium transition-all disabled:opacity-50">
                    {exporting === "docx" ? <Loader2 size={14} className="animate-spin" /> : <Download size={14} />} Download DOCX
                  </button>
                  <button onClick={reset}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-gray-400 hover:text-white text-sm font-medium transition-all">
                    New Report
                  </button>
                </div>
              </div>

              <div className="glass rounded-2xl p-6 prose-dark overflow-y-auto max-h-[60vh]">
                {result.split("\n").map((line, i) => {
                  if (line.startsWith("# "))   return <h1 key={i}>{line.slice(2)}</h1>;
                  if (line.startsWith("## "))  return <h2 key={i}>{line.slice(3)}</h2>;
                  if (line.startsWith("### ")) return <h3 key={i}>{line.slice(4)}</h3>;
                  if (line.startsWith("---"))  return <hr key={i} />;
                  if (!line.trim())            return <br key={i} />;
                  return <p key={i}>{line}</p>;
                })}
              </div>
            </motion.div>
          )}

        </AnimatePresence>
      </div>
    </div>
  );
}
