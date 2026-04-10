import React, { useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Youtube, Upload, Mic, Loader2, CheckCircle2, Music, X, Download, Link2, AlertCircle } from "lucide-react";
import api from "@/utils/api";
import { useTranscribeStore } from "@/store/taskStore";
import { notify, getGoodwillMessage } from "@/components/Notifications";

type Method = "url" | "file";

const STEPS = [
  "Fetching media...",
  "Extracting audio...",
  "Transcribing chunks...",
  "Generating notes...",
  "Finalizing...",
];

export default function TranscriptionHub() {
  const {
    stage, result, error, stepIdx, source,
    setStage, setResult, setError, setStepIdx, setSource, reset,
  } = useTranscribeStore();

  // Local UI state
  const [method, setMethod] = React.useState<Method>("url");
  const [url, setUrl] = React.useState("");
  const [file, setFile] = React.useState<File | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Resume animation if we navigate back while processing
  useEffect(() => {
    if (stage === "processing") {
      intervalRef.current = setInterval(() => {
        setStepIdx(Math.min(useTranscribeStore.getState().stepIdx + 1, STEPS.length - 1));
      }, 4000);
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [stage]);

  const handleTranscribe = async () => {
    if (method === "url" && !url.trim()) return;
    if (method === "file" && !file) return;

    setStage("processing");
    setStepIdx(0);
    setError("");
    setSource(method === "url" ? url : (file?.name || "uploaded file"));

    notify.info("🙏 Thank you! Transcription started — you can navigate away and come back.");

    intervalRef.current = setInterval(() => {
      setStepIdx(Math.min(useTranscribeStore.getState().stepIdx + 1, STEPS.length - 1));
    }, 4000);

    // Goodwill messages
    const goodwillRef = { current: 0 };
    const gwInterval = setInterval(() => {
      notify.info(getGoodwillMessage(goodwillRef.current++));
    }, 30000);

    const fd = new FormData();
    if (method === "url") fd.append("youtube_url", url);
    else if (file) fd.append("file", file);

    try {
      const res = await api.post("/transcribe", fd);
      if (intervalRef.current) clearInterval(intervalRef.current);
      clearInterval(gwInterval);
      setResult(res.data.result);
      setStage("done");
      notify.celebrate("🎉 Transcription complete! Your notes are ready.");
    } catch (e: any) {
      if (intervalRef.current) clearInterval(intervalRef.current);
      clearInterval(gwInterval);
      const msg = e?.response?.data?.detail || "Transcription failed. Check your configuration.";
      setError(msg);
      setStage("error");
      notify.error(msg.slice(0, 80));
    }
  };

  const handleDownload = () => {
    const blob = new Blob([result], { type: "text/plain" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `academix_transcript_${Date.now()}.txt`;
    a.click();
    notify.success("Downloaded transcript");
  };

  return (
    <div className="h-full flex flex-col overflow-hidden relative z-10">
      {/* Header */}
      <div className="shrink-0 px-8 pt-8 pb-5 border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-cyan-700 flex items-center justify-center shadow-lg shadow-blue-900/40">
            <Youtube size={18} className="text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-white">Transcription Hub</h1>
            <p className="text-xs text-gray-500">Paste a YouTube link or upload any audio/video file</p>
          </div>
          {stage === "processing" && (
            <div className="ml-auto flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-500/20 border border-blue-500/30">
              <Loader2 size={12} className="animate-spin text-blue-400" />
              <span className="text-xs text-blue-300 font-medium">Transcribing...</span>
            </div>
          )}
          {stage === "done" && (
            <div className="ml-auto flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/20 border border-emerald-500/30">
              <CheckCircle2 size={12} className="text-emerald-400" />
              <span className="text-xs text-emerald-300 font-medium">Transcript Ready</span>
            </div>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        <AnimatePresence mode="wait">

          {/* ── INPUT ── */}
          {(stage === "idle" || stage === "error") && (
            <motion.div key="input" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="p-8 grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-6xl">
              <div className="space-y-4">
                {/* Method toggle */}
                <div className="glass rounded-2xl p-1 flex gap-1">
                  {(["url", "file"] as Method[]).map((m) => (
                    <button key={m} onClick={() => setMethod(m)}
                      className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-medium transition-all ${
                        method === m ? "bg-blue-600/30 border border-blue-500/30 text-white" : "text-gray-500 hover:text-gray-300"}`}>
                      {m === "url" ? <Link2 size={14} /> : <Upload size={14} />}
                      {m === "url" ? "YouTube / URL" : "Upload File"}
                    </button>
                  ))}
                </div>

                <div className="glass rounded-2xl p-6 space-y-4">
                  {method === "url" ? (
                    <div className="space-y-3">
                      <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Video URL</label>
                      <div className="flex items-center gap-3 rounded-xl px-4 py-3 border border-white/10 focus-within:border-blue-500/50 transition-colors"
                        style={{ background: "rgba(255,255,255,0.06)" }}>
                        <Youtube size={16} className="text-blue-400 shrink-0" />
                        <input value={url} onChange={(e) => setUrl(e.target.value)}
                          placeholder="https://www.youtube.com/watch?v=..."
                          className="flex-1 text-sm outline-none"
                          style={{ background: "transparent", color: "#fff" }} />
                        {url && <button onClick={() => setUrl("")}><X size={14} className="text-gray-600 hover:text-gray-400" /></button>}
                      </div>
                      <p className="text-xs text-gray-600">Supports YouTube and direct audio/video URLs</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Upload File</label>
                      <div onClick={() => fileRef.current?.click()}
                        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
                          file ? "border-blue-500/50 bg-blue-500/5" : "border-white/10 hover:border-blue-500/30"}`}>
                        <input ref={fileRef} type="file" accept=".mp4,.avi,.mov,.mkv,.mp3,.wav,.m4a" className="hidden"
                          onChange={(e) => setFile(e.target.files?.[0] || null)} />
                        {file ? (
                          <div className="space-y-2">
                            <Music size={28} className="mx-auto text-blue-400" />
                            <p className="text-sm font-medium text-white">{file.name}</p>
                            <button onClick={(e) => { e.stopPropagation(); setFile(null); }}
                              className="text-xs text-red-400 flex items-center gap-1 mx-auto"><X size={12} /> Remove</button>
                          </div>
                        ) : (
                          <div className="space-y-2">
                            <Music size={28} className="mx-auto text-gray-600" />
                            <p className="text-sm text-gray-500">MP4, AVI, MOV, MP3, WAV, M4A</p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {stage === "error" && (
                  <div className="flex items-start gap-3 bg-red-500/10 border border-red-500/20 rounded-xl p-4">
                    <AlertCircle size={16} className="text-red-400 shrink-0 mt-0.5" />
                    <p className="text-sm text-red-300">{error}</p>
                  </div>
                )}

                <button onClick={handleTranscribe}
                  disabled={(method === "url" && !url.trim()) || (method === "file" && !file)}
                  className="w-full py-4 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-700 hover:from-blue-500 hover:to-cyan-600 disabled:opacity-40 disabled:cursor-not-allowed font-bold text-sm transition-all shadow-lg shadow-blue-900/30 flex items-center justify-center gap-2">
                  <Mic size={16} /> Start Transcription
                </button>
              </div>

              <div className="glass rounded-2xl p-6 flex flex-col items-center justify-center min-h-[400px] text-center space-y-3">
                <Mic size={48} className="text-gray-700" />
                <p className="text-gray-500 font-medium">Transcript will appear here</p>
                <p className="text-xs text-gray-700 max-w-xs">Provide a URL or upload a file, then click Start Transcription</p>
              </div>
            </motion.div>
          )}

          {/* ── PROCESSING ── */}
          {stage === "processing" && (
            <motion.div key="processing" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center min-h-[60vh] p-8 space-y-8">
              <div className="text-center space-y-3">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-600 to-cyan-700 flex items-center justify-center mx-auto shadow-lg shadow-blue-900/40 animate-pulse">
                  <Mic size={28} className="text-white" />
                </div>
                <h2 className="text-xl font-bold text-white">Transcribing...</h2>
                <p className="text-sm text-gray-500">{source ? `Source: ${source}` : "Processing your media file"}</p>
              </div>

              <div className="w-full max-w-md space-y-3">
                {STEPS.map((step, i) => (
                  <motion.div key={step} initial={{ opacity: 0, x: -20 }} animate={{ opacity: i <= stepIdx ? 1 : 0.3, x: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                      i < stepIdx  ? "bg-emerald-500/10 border border-emerald-500/20" :
                      i === stepIdx ? "bg-blue-500/10 border border-blue-500/20" :
                      "bg-white/5 border border-white/5"}`}>
                    {i < stepIdx  ? <CheckCircle2 size={16} className="text-emerald-400 shrink-0" /> :
                     i === stepIdx ? <Loader2 size={16} className="text-blue-400 animate-spin shrink-0" /> :
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
                    <CheckCircle2 size={16} className="text-emerald-400" />
                  </div>
                  <div>
                    <p className="font-semibold text-white text-sm">Transcription Complete</p>
                    <p className="text-xs text-gray-500">{source && `Source: ${source}`}</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button onClick={handleDownload}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-600/20 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-600/30 text-sm font-medium transition-all">
                    <Download size={14} /> Download
                  </button>
                  <button onClick={reset}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-gray-400 hover:text-white text-sm font-medium transition-all">
                    New Transcription
                  </button>
                </div>
              </div>

              <div className="glass rounded-2xl p-6 overflow-y-auto max-h-[60vh]">
                <pre className="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap font-mono">{result}</pre>
              </div>
            </motion.div>
          )}

        </AnimatePresence>
      </div>
    </div>
  );
}
