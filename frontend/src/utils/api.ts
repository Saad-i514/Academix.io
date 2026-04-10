import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 min — crew tasks can take a while
});

// Attach all user API keys from localStorage to every request
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    try {
      const stored = localStorage.getItem("academix_keys");
      if (stored) {
        const keys = JSON.parse(stored);
        if (keys.openai)  config.headers["X-OpenAI-Key"]  = keys.openai;
        if (keys.groq)    config.headers["X-Groq-Key"]    = keys.groq;
        if (keys.serper)  config.headers["X-Serper-Key"]  = keys.serper;
      }
    } catch {
      // ignore parse errors
    }
  }
  return config;
});

export default api;
