import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Settings, Save, ShieldCheck, Key, CheckCircle, Eye, EyeOff, AlertCircle, ExternalLink } from "lucide-react";
import api from "@/utils/api";
import { notify } from "@/components/Notifications";

interface Keys {
  openai: string;
  groq: string;
  serper: string;
}

function KeyField({
  label, placeholder, value, onChange, hint, required,
}: {
  label: string; placeholder: string; value: string;
  onChange: (v: string) => void; hint?: string; required?: boolean;
}) {
  const [show, setShow] = useState(false);
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider">{label}</label>
        {required && <span className="text-[10px] px-1.5 py-0.5 rounded bg-violet-500/20 text-violet-300 border border-violet-500/20">Required</span>}
      </div>
      <div
        className="flex items-center gap-2 rounded-xl px-4 py-3 border transition-colors focus-within:border-violet-500/50"
        style={{ background: "rgba(255,255,255,0.06)", borderColor: value ? "rgba(16,185,129,0.3)" : "rgba(255,255,255,0.1)" }}
      >
        <Key size={14} className={value ? "text-emerald-400 shrink-0" : "text-gray-600 shrink-0"} />
        <input
          type={show ? "text" : "password"}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="flex-1 text-sm outline-none"
          style={{ background: "transparent", color: "#fff" }}
        />
        {value && <CheckCircle size={14} className="text-emerald-400 shrink-0" />}
        <button onClick={() => setShow(!show)} className="text-gray-600 hover:text-gray-400 transition-colors ml-1">
          {show ? <EyeOff size={14} /> : <Eye size={14} />}
        </button>
      </div>
      {hint && <p className="text-xs text-gray-600">{hint}</p>}
    </div>
  );
}

export default function SettingsPage() {
  const [keys, setKeys] = useState<Keys>({ openai: "", groq: "", serper: "" });
  const [saved, setSaved] = useState(false);
  const [backendStatus, setBackendStatus] = useState<"checking" | "ok" | "error">("checking");

  useEffect(() => {
    const stored = localStorage.getItem("academix_keys");
    if (stored) {
      try { setKeys({ openai: "", groq: "", serper: "", ...JSON.parse(stored) }); }
      catch { /* ignore */ }
    }
    // Check backend health
    api.get("/health").then(() => setBackendStatus("ok")).catch(() => setBackendStatus("error"));
  }, []);

  const handleSave = () => {
    localStorage.setItem("academix_keys", JSON.stringify(keys));
    setSaved(true);
    notify.celebrate("🔑 API keys saved! You're all set to use Academix.");
    setTimeout(() => setSaved(false), 2500);
  };

  const hasMinKeys = !!(keys.openai || keys.groq);

  return (
    <div className="h-full overflow-y-auto relative z-10">
      {/* Header */}
      <div className="shrink-0 px-8 pt-8 pb-5 border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-gray-600 to-gray-700 flex items-center justify-center">
            <Settings size={18} className="text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-white">Settings</h1>
            <p className="text-xs text-gray-500">Configure your API keys — stored locally, never on our servers</p>
          </div>
        </div>
      </div>

      <div className="p-8 max-w-2xl space-y-6">

        {/* Backend status */}
        <div className={`flex items-center gap-3 rounded-xl p-4 border ${
          backendStatus === "ok"
            ? "bg-emerald-500/10 border-emerald-500/20"
            : backendStatus === "error"
            ? "bg-red-500/10 border-red-500/20"
            : "bg-white/5 border-white/10"
        }`}>
          <div className={`w-2 h-2 rounded-full ${
            backendStatus === "ok" ? "bg-emerald-400 animate-pulse" :
            backendStatus === "error" ? "bg-red-400" : "bg-yellow-400 animate-pulse"
          }`} />
          <p className="text-sm text-gray-300">
            {backendStatus === "ok" ? "Backend connected and ready" :
             backendStatus === "error" ? "Backend unreachable — check your connection" :
             "Checking backend connection..."}
          </p>
        </div>

        {/* Warning if no keys */}
        {!hasMinKeys && (
          <div className="flex items-start gap-3 bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-4">
            <AlertCircle size={16} className="text-yellow-400 shrink-0 mt-0.5" />
            <p className="text-sm text-yellow-300">
              You need at least one LLM key (OpenAI or Groq) to use Academix. Add your keys below.
            </p>
          </div>
        )}

        {/* Security notice */}
        <div className="flex items-start gap-3 bg-violet-500/10 border border-violet-500/20 rounded-xl p-4">
          <ShieldCheck size={16} className="text-violet-400 shrink-0 mt-0.5" />
          <p className="text-sm text-gray-400">
            Keys are stored in your browser's localStorage and sent directly to the backend only when you make a request. They are never logged or stored on our servers.
          </p>
        </div>

        {/* LLM Keys */}
        <div className="glass rounded-2xl p-6 space-y-5">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-white text-sm">LLM Keys</h3>
            <span className="text-xs text-gray-600">At least one required</span>
          </div>

          <KeyField
            label="OpenAI API Key"
            placeholder="sk-proj-..."
            value={keys.openai}
            onChange={(v) => setKeys({ ...keys, openai: v })}
            hint="Powers GPT-4o-mini for report generation and chat"
            required
          />
          <KeyField
            label="Groq API Key"
            placeholder="gsk_..."
            value={keys.groq}
            onChange={(v) => setKeys({ ...keys, groq: v })}
            hint="Alternative to OpenAI — uses Llama 3 70B (free tier available)"
          />
        </div>

        {/* Search Key */}
        <div className="glass rounded-2xl p-6 space-y-5">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-white text-sm">Search Key</h3>
            <a
              href="https://serper.dev"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-xs text-violet-400 hover:text-violet-300 transition-colors"
            >
              Get free key <ExternalLink size={10} />
            </a>
          </div>

          <KeyField
            label="Serper API Key"
            placeholder="your-serper-key..."
            value={keys.serper}
            onChange={(v) => setKeys({ ...keys, serper: v })}
            hint="Enables internet search for agents — get 2,500 free searches/month at serper.dev"
          />
        </div>

        {/* Save */}
        <motion.button
          onClick={handleSave}
          whileTap={{ scale: 0.98 }}
          disabled={!hasMinKeys}
          className={`w-full py-3.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition-all ${
            saved
              ? "bg-emerald-600/20 border border-emerald-500/30 text-emerald-400"
              : hasMinKeys
              ? "bg-gradient-to-r from-violet-600 to-purple-700 hover:from-violet-500 hover:to-purple-600 text-white shadow-lg shadow-violet-900/30"
              : "bg-white/5 border border-white/10 text-gray-600 cursor-not-allowed"
          }`}
        >
          {saved ? <><CheckCircle size={16} /> Saved Successfully</> : <><Save size={16} /> Save API Keys</>}
        </motion.button>

        {/* Where to get keys */}
        <div className="glass rounded-2xl p-6 space-y-4">
          <h3 className="font-semibold text-white text-sm">Where to get your keys</h3>
          <div className="space-y-3">
            {[
              { name: "OpenAI", url: "https://platform.openai.com/api-keys", desc: "GPT-4o-mini — best quality" },
              { name: "Groq", url: "https://console.groq.com/keys", desc: "Llama 3 70B — free tier" },
              { name: "Serper", url: "https://serper.dev", desc: "Google Search API — 2,500 free/month" },
            ].map(({ name, url, desc }) => (
              <a
                key={name}
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-between p-3 rounded-xl bg-white/3 hover:bg-white/6 border border-white/8 transition-all group"
                style={{ background: "rgba(255,255,255,0.03)" }}
              >
                <div>
                  <p className="text-sm font-medium text-white">{name}</p>
                  <p className="text-xs text-gray-500">{desc}</p>
                </div>
                <ExternalLink size={14} className="text-gray-600 group-hover:text-violet-400 transition-colors" />
              </a>
            ))}
          </div>
        </div>

        {/* About */}
        <div className="glass rounded-2xl p-6 space-y-3">
          <h3 className="font-semibold text-white text-sm">About Academix.io</h3>
          <div className="space-y-2 text-sm text-gray-500">
            <p>Version: <span className="text-gray-300">2.0.0</span></p>
            <p>Built by: <span className="text-gray-300">Muhammad Saad bin Mazhar</span></p>
            <p>Frontend: <span className="text-gray-300">Next.js 14 · Deployed on Vercel</span></p>
            <p>Backend: <span className="text-gray-300">FastAPI + CrewAI · Deployed on Railway</span></p>
          </div>
        </div>

      </div>
    </div>
  );
}
