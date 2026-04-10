import React, { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { Send, Bot, User, FileText, Youtube, Zap, BookOpen, Loader2, Sparkles, Rocket, Brain, GraduationCap } from "lucide-react";
import Link from "next/link";
import api from "@/utils/api";
import { notify } from "@/components/Notifications";

interface Message { role: "user" | "assistant"; content: string; }

const FEATURES = [
  {
    href: "/report",
    icon: GraduationCap,
    color: "from-violet-600 to-purple-700",
    glow: "shadow-violet-900/40",
    badge: "AI Powered",
    title: "Report Studio",
    desc: "Upload any lab manual or assignment. Our AI agents scan the document and generate a complete, structured academic report automatically.",
    cta: "Open Studio →",
  },
  {
    href: "/transcribe",
    icon: Brain,
    color: "from-blue-600 to-cyan-700",
    glow: "shadow-blue-900/40",
    badge: "Fast Pipeline",
    title: "Transcription Hub",
    desc: "Paste a YouTube link or upload any audio/video file. Get full transcription and study notes in minutes.",
    cta: "Open Hub →",
  },
];

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Welcome to Academix! 🎓 I'm your AI-powered academic assistant, ready to help you excel in your studies. Whether you need help creating reports, transcribing lectures, or answering academic questions—I've got you covered. What would you like to work on today?",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Welcome notification on first visit
  useEffect(() => {
    const welcomed = sessionStorage.getItem("academix_welcomed");
    if (!welcomed) {
      setTimeout(() => notify.info("👋 Welcome to Academix.io — your AI academic assistant!"), 800);
      sessionStorage.setItem("academix_welcomed", "1");
    }
  }, []);

  const send = async () => {
    const text = input.trim();
    if (!text || loading) return;
    setInput("");
    setMessages((p) => [...p, { role: "user", content: text }]);
    setLoading(true);
    try {
      const fd = new FormData();
      fd.append("message", text);
      const res = await api.post("/chat", fd);
      setMessages((p) => [...p, { role: "assistant", content: res.data.response }]);
    } catch {
      notify.error("Connection issue — check your API keys in Settings");
      setMessages((p) => [...p, { role: "assistant", content: "I'm here to help with academic tasks! Try asking about report creation or transcription." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden relative z-10">
      {/* Top bar */}
      <div className="shrink-0 px-4 sm:px-6 md:px-8 pt-6 md:pt-8 pb-3 md:pb-4 border-b border-white/5">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-3xl sm:text-4xl font-black gradient-text tracking-tight">Academix.io</h1>
          <p className="text-gray-500 text-xs sm:text-sm mt-1">Your AI-powered academic automation platform</p>
        </motion.div>
      </div>

      {/* Body: two columns */}
      <div className="flex-1 flex overflow-hidden">

        {/* Left: Feature cards + stats */}
        <div className="hidden lg:flex flex-col w-[420px] xl:w-[460px] shrink-0 border-r border-white/5 p-6 gap-5 overflow-y-auto">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-widest">Quick Access</p>

          {FEATURES.map(({ href, icon: Icon, color, glow, badge, title, desc, cta }) => (
            <Link key={href} href={href}>
              <motion.div
                whileHover={{ y: -2, scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                className="glass glass-hover rounded-2xl p-5 cursor-pointer group"
              >
                <div className="flex items-start gap-4">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center shadow-lg ${glow} shrink-0`}>
                    <Icon size={22} className="text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold text-white text-sm">{title}</span>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-violet-500/20 text-violet-300 border border-violet-500/20">{badge}</span>
                    </div>
                    <p className="text-xs text-gray-500 leading-relaxed">{desc}</p>
                    <span className="text-xs font-semibold text-violet-400 mt-2 inline-block group-hover:text-violet-300 transition-colors">{cta}</span>
                  </div>
                </div>
              </motion.div>
            </Link>
          ))}

          {/* Stats row */}
          <div className="grid grid-cols-3 gap-3 mt-2">
            {[
              { icon: Rocket, label: "One Click", sub: "Reports" },
              { icon: Brain, label: "AI Agents", sub: "Powered" },
              { icon: Sparkles, label: "Any Video", sub: "Transcribed" },
            ].map(({ icon: Icon, label, sub }) => (
              <div key={label} className="glass rounded-xl p-3 text-center hover:bg-white/10 transition-colors cursor-pointer">
                <Icon size={18} className="text-violet-400 mx-auto mb-1" />
                <p className="text-xs font-bold text-white">{label}</p>
                <p className="text-[10px] text-gray-500">{sub}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Chat */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="shrink-0 px-4 sm:px-6 py-3 border-b border-white/5 flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs sm:text-sm font-medium text-gray-400">Academix Agent</span>
            <span className="hidden sm:inline text-xs text-gray-600 ml-auto">Academic queries only</span>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-3 sm:px-4 md:px-6 py-4 space-y-3 sm:space-y-4">
            {messages.map((msg, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
                className={`flex gap-2 sm:gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}
              >
                <div className={`w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center shrink-0 ${
                  msg.role === "user"
                    ? "bg-violet-600"
                    : "bg-gradient-to-br from-violet-700 to-purple-800"
                }`}>
                  {msg.role === "user" ? <User size={14} /> : <Bot size={14} />}
                </div>
                <div className={`max-w-[85%] sm:max-w-[75%] px-3 sm:px-4 py-2.5 sm:py-3 rounded-2xl text-xs sm:text-sm leading-relaxed ${
                  msg.role === "user"
                    ? "bg-violet-600/20 border border-violet-500/20 text-white rounded-tr-sm"
                    : "bg-white/5 border border-white/8 text-gray-300 rounded-tl-sm"
                }`}>
                  {msg.content}
                </div>
              </motion.div>
            ))}
            {loading && (
              <div className="flex gap-2 sm:gap-3">
                <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-gradient-to-br from-violet-700 to-purple-800 flex items-center justify-center shrink-0">
                  <Bot size={14} />
                </div>
                <div className="bg-white/5 border border-white/8 px-3 sm:px-4 py-2.5 sm:py-3 rounded-2xl rounded-tl-sm flex items-center gap-2">
                  <Loader2 size={14} className="animate-spin text-violet-400" />
                  <span className="text-xs sm:text-sm text-gray-500">Thinking...</span>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="shrink-0 px-3 sm:px-4 md:px-6 py-3 sm:py-4 border-t border-white/5">
            <div className="flex gap-2 sm:gap-3 items-end">
              <div className="flex-1 glass rounded-xl sm:rounded-2xl px-3 sm:px-4 py-2.5 sm:py-3 flex items-center gap-2">
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && send()}
                  placeholder="Ask an academic question..."
                  className="flex-1 text-xs sm:text-sm outline-none"
                  style={{ background: 'transparent', color: '#fff' }}
                />
              </div>
              <button
                onClick={send}
                disabled={loading || !input.trim()}
                className="w-10 h-10 sm:w-11 sm:h-11 rounded-xl bg-violet-600 hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center transition-all shrink-0 active:scale-95"
              >
                <Send size={15} className="sm:w-4 sm:h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
