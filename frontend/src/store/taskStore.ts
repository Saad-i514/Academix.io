/**
 * Global persistent state for Report and Transcription tasks.
 * Using Zustand so state survives page navigation within the SPA.
 */
import { create } from "zustand";

type Stage = "idle" | "processing" | "done" | "error";

// ── Report Store ──────────────────────────────────────────────────────────────
interface ReportState {
  stage: Stage;
  result: string;
  error: string;
  stepIdx: number;
  fileName: string;
  setStage:    (s: Stage)   => void;
  setResult:   (r: string)  => void;
  setError:    (e: string)  => void;
  setStepIdx:  (n: number)  => void;
  setFileName: (f: string)  => void;
  reset: () => void;
}

export const useReportStore = create<ReportState>((set) => ({
  stage:    "idle",
  result:   "",
  error:    "",
  stepIdx:  0,
  fileName: "",
  setStage:    (stage)    => set({ stage }),
  setResult:   (result)   => set({ result }),
  setError:    (error)    => set({ error }),
  setStepIdx:  (stepIdx)  => set({ stepIdx }),
  setFileName: (fileName) => set({ fileName }),
  reset: () => set({ stage: "idle", result: "", error: "", stepIdx: 0, fileName: "" }),
}));

// ── Transcribe Store ──────────────────────────────────────────────────────────
interface TranscribeState {
  stage:    Stage;
  result:   string;
  error:    string;
  stepIdx:  number;
  source:   string;   // URL or filename
  setStage:   (s: Stage)  => void;
  setResult:  (r: string) => void;
  setError:   (e: string) => void;
  setStepIdx: (n: number) => void;
  setSource:  (s: string) => void;
  reset: () => void;
}

export const useTranscribeStore = create<TranscribeState>((set) => ({
  stage:   "idle",
  result:  "",
  error:   "",
  stepIdx: 0,
  source:  "",
  setStage:   (stage)   => set({ stage }),
  setResult:  (result)  => set({ result }),
  setError:   (error)   => set({ error }),
  setStepIdx: (stepIdx) => set({ stepIdx }),
  setSource:  (source)  => set({ source }),
  reset: () => set({ stage: "idle", result: "", error: "", stepIdx: 0, source: "" }),
}));
