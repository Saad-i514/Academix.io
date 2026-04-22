import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 1800000, // 30 min — supports transcription of 1-hour videos
});

// Attach all user API keys from localStorage to every request
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    try {
      const stored = localStorage.getItem("academix_keys");
      if (stored) {
        const keys = JSON.parse(stored);
        if (keys.openai)              config.headers["X-OpenAI-Key"]         = keys.openai;
        if (keys.groq)                config.headers["X-Groq-Key"]           = keys.groq;
        if (keys.serper)              config.headers["X-Serper-Key"]         = keys.serper;
        if (keys.notion_api_key)      config.headers["X-Notion-API-Key"]     = keys.notion_api_key;
        if (keys.notion_database_id)  config.headers["X-Notion-Database-ID"] = keys.notion_database_id;
        if (keys.adobe_client_id)     config.headers["X-Adobe-Client-ID"]    = keys.adobe_client_id;
        if (keys.adobe_client_secret) config.headers["X-Adobe-Client-Secret"]= keys.adobe_client_secret;
        if (keys.octave_api_key)      config.headers["X-Octave-API-Key"]     = keys.octave_api_key;
      }
    } catch {
      // ignore parse errors
    }
  }
  return config;
});

export default api;
