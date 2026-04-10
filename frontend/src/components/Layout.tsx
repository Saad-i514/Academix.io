import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/router";
import Head from "next/head";
import { motion, AnimatePresence } from "framer-motion";
import {
  GraduationCap, FileText, Youtube, Clock, Settings,
  Menu, X, Sparkles, Loader2, CheckCircle, Home, Brain,
} from "lucide-react";
import { useReportStore, useTranscribeStore } from "@/store/taskStore";

const NAV = [
  { href: "/",          icon: Home,         label: "Dashboard",        color: "text-violet-400" },
  { href: "/report",    icon: FileText,     label: "Report Studio",    color: "text-purple-400" },
  { href: "/transcribe",icon: Brain,        label: "Transcribe",       color: "text-blue-400"   },
  { href: "/history",   icon: Clock,        label: "Memory",           color: "text-pink-400"   },
  { href: "/settings",  icon: Settings,     label: "Settings",         color: "text-gray-400"   },
];

interface LayoutProps {
  children: React.ReactNode;
  title?: string;
}

export default function Layout({ children, title = "Academix.io" }: LayoutProps) {
  const router = useRouter();
  const [mobileOpen, setMobileOpen] = useState(false);
  const reportStage = useReportStore((s) => s.stage);
  const transcribeStage = useTranscribeStore((s) => s.stage);

  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className="flex min-h-screen bg-[#080C14] text-white">
        {/* ── Sidebar ── */}
        <aside className="hidden md:flex flex-col fixed left-0 top-0 h-full w-64 lg:w-72 bg-[#0D1117] border-r border-white/5 z-40">
          {/* Logo */}
          <Link href="/">
            <div className="flex items-center gap-3 px-6 py-6 border-b border-white/5 cursor-pointer group">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-600 to-purple-700 flex items-center justify-center shadow-lg shadow-violet-900/40 group-hover:scale-105 transition-transform">
                <GraduationCap size={18} className="text-white" />
              </div>
              <span className="text-lg font-bold tracking-tight group-hover:text-violet-300 transition-colors">
                Academix<span className="text-violet-400">.io</span>
              </span>
            </div>
          </Link>

          {/* Nav */}
          <nav className="flex-1 px-3 py-6 space-y-1">
            {NAV.map(({ href, icon: Icon, label, color }) => {
              const active = router.pathname === href;
              // Status indicators for processing pages
              const isReportProcessing   = href === "/report"     && reportStage === "processing";
              const isReportDone         = href === "/report"     && reportStage === "done";
              const isTranscribeProcessing = href === "/transcribe" && transcribeStage === "processing";
              const isTranscribeDone     = href === "/transcribe" && transcribeStage === "done";
              return (
                <Link key={href} href={href}>
                  <div className={`flex items-center gap-3 px-4 py-3 rounded-xl cursor-pointer transition-all duration-200 group
                    ${active
                      ? "bg-violet-600/20 border border-violet-500/30 text-white shadow-lg shadow-violet-900/20"
                      : "hover:bg-white/5 text-gray-400 hover:text-white border border-transparent"
                    }`}>
                    <Icon size={18} className={active ? "text-violet-400" : color} />
                    <span className="text-sm font-medium">{label}</span>
                    <div className="ml-auto flex items-center gap-1">
                      {(isReportProcessing || isTranscribeProcessing) && (
                        <Loader2 size={12} className="animate-spin text-violet-400" />
                      )}
                      {(isReportDone || isTranscribeDone) && (
                        <CheckCircle size={12} className="text-emerald-400" />
                      )}
                      {active && !isReportProcessing && !isReportDone && !isTranscribeProcessing && !isTranscribeDone && (
                        <motion.div layoutId="activeIndicator" className="w-1.5 h-1.5 rounded-full bg-violet-400" />
                      )}
                    </div>
                  </div>
                </Link>
              );
            })}
          </nav>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-white/5">
            <p className="text-xs text-gray-600">Powered by AI</p>
            <p className="text-xs text-gray-700 mt-0.5">v2.0 · Production</p>
          </div>
        </aside>

        {/* ── Mobile Header ── */}
        <div className="md:hidden fixed top-0 left-0 right-0 h-16 bg-[#0D1117]/95 backdrop-blur-lg border-b border-white/5 flex items-center justify-between px-4 z-40">
          <Link href="/">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-purple-700 flex items-center justify-center shadow-lg shadow-violet-900/40">
                <GraduationCap size={16} className="text-white" />
              </div>
              <span className="font-bold text-base sm:text-lg">Academix<span className="text-violet-400">.io</span></span>
            </div>
          </Link>
          <button onClick={() => setMobileOpen(true)} className="p-2 rounded-lg hover:bg-white/5 active:scale-95 transition-all">
            <Menu size={20} />
          </button>
        </div>

        {/* ── Mobile Drawer ── */}
        <AnimatePresence>
          {mobileOpen && (
            <>
              <motion.div
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 md:hidden"
                onClick={() => setMobileOpen(false)}
              />
              <motion.div
                initial={{ x: -280 }} animate={{ x: 0 }} exit={{ x: -280 }}
                transition={{ type: "spring", damping: 25, stiffness: 300 }}
                className="fixed left-0 top-0 h-full w-72 bg-[#0D1117] border-r border-white/5 z-50 md:hidden shadow-2xl"
              >
                <div className="flex items-center justify-between px-6 py-5 border-b border-white/5">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-purple-700 flex items-center justify-center shadow-lg shadow-violet-900/40">
                      <GraduationCap size={16} className="text-white" />
                    </div>
                    <span className="font-bold text-lg">Academix<span className="text-violet-400">.io</span></span>
                  </div>
                  <button onClick={() => setMobileOpen(false)} className="p-1.5 rounded-lg hover:bg-white/5 active:scale-95 transition-all">
                    <X size={18} />
                  </button>
                </div>
                <nav className="px-3 py-4 space-y-1">
                  {NAV.map(({ href, icon: Icon, label, color }) => {
                    const active = router.pathname === href;
                    return (
                      <Link key={href} href={href}>
                        <div
                          onClick={() => setMobileOpen(false)}
                          className={`flex items-center gap-3 px-4 py-3 rounded-xl cursor-pointer transition-all ${
                            active
                              ? "bg-violet-600/20 border border-violet-500/30 text-white"
                              : "hover:bg-white/5 text-gray-400 hover:text-white border border-transparent"
                          }`}
                        >
                          <Icon size={18} className={active ? "text-violet-400" : color} />
                          <span className="text-sm font-medium">{label}</span>
                        </div>
                      </Link>
                    );
                  })}
                </nav>
                <div className="absolute bottom-0 left-0 right-0 px-6 py-4 border-t border-white/5">
                  <p className="text-xs text-gray-600">Powered by AI</p>
                  <p className="text-xs text-gray-700 mt-0.5">v2.0 · Production</p>
                </div>
              </motion.div>
            </>
          )}
        </AnimatePresence>

        {/* ── Page Content ── */}
        <main className="flex-1 md:ml-64 lg:ml-72 pt-16 md:pt-0 min-h-screen">
          <motion.div
            key={router.pathname}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25 }}
            className="h-full"
          >
            {children}
          </motion.div>
        </main>
      </div>
    </>
  );
}
