import toast, { Toaster } from "react-hot-toast";
import { CheckCircle, AlertCircle, Info, Loader2, PartyPopper } from "lucide-react";

// ── Toast helpers ─────────────────────────────────────────────────────────────

export const notify = {
  success: (msg: string) =>
    toast.custom((t) => (
      <div className={`flex items-center gap-3 px-5 py-3.5 rounded-2xl shadow-2xl border transition-all duration-300 ${
        t.visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-2"
      }`} style={{ background: "rgba(16,185,129,0.15)", borderColor: "rgba(16,185,129,0.3)", backdropFilter: "blur(16px)" }}>
        <CheckCircle size={18} className="text-emerald-400 shrink-0" />
        <span className="text-sm font-medium text-white">{msg}</span>
      </div>
    ), { duration: 3500 }),

  error: (msg: string) =>
    toast.custom((t) => (
      <div className={`flex items-center gap-3 px-5 py-3.5 rounded-2xl shadow-2xl border transition-all duration-300 ${
        t.visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-2"
      }`} style={{ background: "rgba(239,68,68,0.15)", borderColor: "rgba(239,68,68,0.3)", backdropFilter: "blur(16px)" }}>
        <AlertCircle size={18} className="text-red-400 shrink-0" />
        <span className="text-sm font-medium text-white">{msg}</span>
      </div>
    ), { duration: 5000 }),

  info: (msg: string) =>
    toast.custom((t) => (
      <div className={`flex items-center gap-3 px-5 py-3.5 rounded-2xl shadow-2xl border transition-all duration-300 ${
        t.visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-2"
      }`} style={{ background: "rgba(139,92,246,0.15)", borderColor: "rgba(139,92,246,0.3)", backdropFilter: "blur(16px)" }}>
        <Info size={18} className="text-violet-400 shrink-0" />
        <span className="text-sm font-medium text-white">{msg}</span>
      </div>
    ), { duration: 4000 }),

  loading: (msg: string) =>
    toast.custom((t) => (
      <div className={`flex items-center gap-3 px-5 py-3.5 rounded-2xl shadow-2xl border transition-all duration-300 ${
        t.visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-2"
      }`} style={{ background: "rgba(30,33,57,0.9)", borderColor: "rgba(139,92,246,0.3)", backdropFilter: "blur(16px)" }}>
        <Loader2 size={18} className="text-violet-400 animate-spin shrink-0" />
        <span className="text-sm font-medium text-white">{msg}</span>
      </div>
    ), { duration: Infinity }),

  celebrate: (msg: string) =>
    toast.custom((t) => (
      <div className={`flex items-center gap-3 px-5 py-4 rounded-2xl shadow-2xl border transition-all duration-300 ${
        t.visible ? "opacity-100 scale-100" : "opacity-0 scale-95"
      }`} style={{ background: "linear-gradient(135deg, rgba(139,92,246,0.2), rgba(59,130,246,0.2))", borderColor: "rgba(139,92,246,0.4)", backdropFilter: "blur(16px)" }}>
        <span className="text-xl">🎉</span>
        <span className="text-sm font-bold text-white">{msg}</span>
      </div>
    ), { duration: 4000 }),
};

// ── Toaster provider ──────────────────────────────────────────────────────────

export function ToastProvider() {
  return (
    <Toaster
      position="top-right"
      gutter={10}
      containerStyle={{ top: 20, right: 20 }}
    />
  );
}

// ── Goodwill messages shown during long processing ────────────────────────────

const GOODWILL_MESSAGES = [
  "☕ Grab a coffee — our AI agents are working hard for you!",
  "🧠 Our agents are reading, thinking, and writing...",
  "📚 Researching the best sources for your report...",
  "⚡ Almost there — quality takes a moment!",
  "🔬 Running analysis and compiling results...",
  "✍️ Crafting your professional report...",
  "🎯 Ensuring every section meets academic standards...",
  "💡 Finding the best citations for your topic...",
];

export function getGoodwillMessage(index: number): string {
  return GOODWILL_MESSAGES[index % GOODWILL_MESSAGES.length];
}
