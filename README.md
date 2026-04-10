# 🎓 Academix.io

**Your AI-Powered Academic Automation Platform**

Academix is a comprehensive full-stack web application that leverages AI agents to automate academic tasks, including report generation, video transcription, and intelligent academic assistance. Built with Next.js, FastAPI, and powered by CrewAI multi-agent systems.

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Next.js](https://img.shields.io/badge/next.js-14.1.0-black)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Features

### 🤖 AI Academic Assistant
- Interactive chat interface with AI-powered academic support
- Context-aware responses for academic queries
- Real-time conversation with intelligent agents

### 📝 Report Studio (AI-Powered)
- Upload lab manuals or assignments
- Automatic document scanning and analysis
- Complete structured academic report generation
- Export reports in multiple formats (PDF, DOCX, Markdown)
- Citation finding and plagiarism checking
- Grammar and LaTeX rendering support

### 🎥 Transcription Hub (Fast Pipeline)
- YouTube video transcription
- Audio/video file upload support
- Automatic study notes generation
- Fast processing pipeline
- Downloadable transcripts

### 🧠 Advanced AI Tools
- **Code Compilation**: Execute and test code snippets
- **Data Visualization**: Generate charts and graphs
- **Image Creation**: AI-powered image generation
- **Wolfram Integration**: Mathematical computations
- **Web Search**: Real-time information retrieval
- **Notion Integration**: Export to Notion workspace

---

## 🏗️ Architecture

```
academix/
├── frontend/          # Next.js + TypeScript + Tailwind CSS
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Next.js pages
│   │   ├── store/        # Zustand state management
│   │   └── utils/        # API utilities
│   └── public/           # Static assets
│
├── backend/           # FastAPI + Python
│   ├── app/
│   │   ├── llm.py           # LLM integration
│   │   └── report_exporter.py  # Report export logic
│   └── main.py              # FastAPI application
│
└── src/cua/          # CrewAI Multi-Agent System
    ├── config/
    │   ├── agents.yaml      # Agent definitions
    │   └── tasks.yaml       # Task configurations
    ├── tools/               # Custom AI tools
    ├── crew.py              # Crew orchestration
    └── main.py              # Entry point
```

---

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.10 - 3.13
- **Node.js**: 18.x or higher
- **npm** or **yarn**
- **UV** (Python package manager)

### Installation

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd cua
```

#### 2. Backend Setup

```bash
# Install UV (if not already installed)
pip install uv

# Install Python dependencies
crewai install

# Or manually with UV
uv pip install -r requirements.txt
```

#### 3. Frontend Setup

```bash
cd frontend
npm install
# or
yarn install
```

#### 4. Environment Configuration

Create a `.env` file in the root directory:

```env
# OpenAI API Key (Required)
OPENAI_API_KEY=your_openai_api_key_here

# Groq API Key (Optional)
GROQ_API_KEY=your_groq_api_key_here

# Serper API Key (for web search)
SERPER_API_KEY=your_serper_api_key_here

# Other API Keys
WOLFRAM_APP_ID=your_wolfram_app_id
NOTION_API_KEY=your_notion_api_key
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🎯 Running the Application

### Development Mode

#### Start Backend (FastAPI)

```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

#### Start Frontend (Next.js)

```bash
cd frontend
npm run dev
# or
yarn dev
```

Frontend will be available at: `http://localhost:3000`

### Production Mode

#### Build Frontend

```bash
cd frontend
npm run build
npm start
```

#### Run Backend

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 🛠️ Technology Stack

### Frontend
- **Framework**: Next.js 14.1.0
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Lucide React Icons
- **Animations**: Framer Motion
- **Particles**: @tsparticles/react
- **State Management**: Zustand
- **HTTP Client**: Axios

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.10+
- **AI Framework**: CrewAI
- **LLM**: OpenAI GPT / Groq
- **Package Manager**: UV

### AI Tools & Integrations
- OpenAI GPT-4
- Groq LLM
- Serper (Web Search)
- Wolfram Alpha
- Notion API
- YouTube Transcript API
- Whisper (Audio Transcription)

---

## 📁 Project Structure

### Frontend Pages

- `/` - Dashboard with AI chat assistant
- `/report` - Report Studio for document generation
- `/transcribe` - Transcription Hub for video/audio
- `/history` - Memory and conversation history
- `/settings` - API key configuration

### Backend Endpoints

- `POST /chat` - AI chat conversation
- `POST /report/generate` - Generate academic report
- `POST /transcribe` - Transcribe video/audio
- `GET /history` - Retrieve conversation history
- `POST /export` - Export reports (PDF/DOCX)

### AI Agents

Defined in `src/cua/config/agents.yaml`:
- **Research Agent**: Information gathering and analysis
- **Writing Agent**: Content creation and structuring
- **Review Agent**: Quality assurance and editing
- **Citation Agent**: Reference management

---

## 🎨 Features in Detail

### Report Studio
1. Upload lab manual or assignment PDF
2. AI agents analyze document structure
3. Automatic research and content generation
4. Citation finding and plagiarism checking
5. Grammar correction and LaTeX rendering
6. Export in multiple formats

### Transcription Hub
1. Paste YouTube URL or upload audio/video
2. Automatic transcription using Whisper
3. AI-generated study notes
4. Downloadable transcript
5. Fast processing pipeline

### AI Chat Assistant
- Context-aware academic support
- Multi-turn conversations
- Memory persistence
- Real-time responses

---

## 🔧 Configuration

### Agent Configuration

Edit `src/cua/config/agents.yaml` to customize AI agents:

```yaml
research_agent:
  role: "Academic Researcher"
  goal: "Conduct thorough research on academic topics"
  backstory: "Expert researcher with deep knowledge"
  tools:
    - web_search_tool
    - citation_finder_tool
```

### Task Configuration

Edit `src/cua/config/tasks.yaml` to define workflows:

```yaml
research_task:
  description: "Research the given topic thoroughly"
  agent: research_agent
  expected_output: "Comprehensive research report"
```

---

## 🧪 Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Python linting
flake8 src/

# TypeScript linting
cd frontend
npm run lint
```

---

## 📦 Deployment

### Frontend (Vercel)

```bash
cd frontend
vercel deploy
```

### Backend (Railway/Render)

```bash
cd backend
# Configure Procfile and requirements.txt
# Deploy via Railway or Render dashboard
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [CrewAI](https://crewai.com) - Multi-agent AI framework
- [OpenAI](https://openai.com) - GPT models
- [Next.js](https://nextjs.org) - React framework
- [FastAPI](https://fastapi.tiangolo.com) - Python web framework
- [Tailwind CSS](https://tailwindcss.com) - Utility-first CSS

---

## 📞 Support

For questions, issues, or feature requests:

- Open an issue on GitHub
- Contact: [your-email@example.com]

---

**Built with ❤️ using AI and modern web technologies**

