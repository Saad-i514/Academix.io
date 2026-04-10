"""
Generate Academix.io Architecture Diagram
Requires: pip install pillow
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Create image
width, height = 2400, 3000
img = Image.new('RGB', (width, height), color='#0f172a')
draw = ImageDraw.Draw(img)

# Try to use a nice font, fallback to default
try:
    title_font = ImageFont.truetype("arial.ttf", 48)
    heading_font = ImageFont.truetype("arial.ttf", 32)
    text_font = ImageFont.truetype("arial.ttf", 20)
    small_font = ImageFont.truetype("arial.ttf", 16)
except:
    title_font = ImageFont.load_default()
    heading_font = ImageFont.load_default()
    text_font = ImageFont.load_default()
    small_font = ImageFont.load_default()

# Colors
purple = '#8b5cf6'
blue = '#3b82f6'
green = '#10b981'
orange = '#f59e0b'
red = '#ef4444'
pink = '#ec4899'
white = '#ffffff'
gray = '#64748b'

def draw_box(x, y, w, h, color, text, font=text_font):
    """Draw a rounded rectangle with text"""
    draw.rounded_rectangle([x, y, x+w, y+h], radius=10, fill=color, outline=white, width=2)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    draw.text((x + (w-text_w)//2, y + (h-text_h)//2), text, fill=white, font=font)

def draw_arrow(x1, y1, x2, y2, color=white):
    """Draw an arrow from (x1,y1) to (x2,y2)"""
    draw.line([x1, y1, x2, y2], fill=color, width=3)
    # Arrow head
    angle = 0.5
    length = 15
    import math
    dx = x2 - x1
    dy = y2 - y1
    norm = math.sqrt(dx*dx + dy*dy)
    if norm > 0:
        dx /= norm
        dy /= norm
        draw.line([x2, y2, x2 - length*(dx*math.cos(angle) + dy*math.sin(angle)), 
                   y2 - length*(dy*math.cos(angle) - dx*math.sin(angle))], fill=color, width=3)
        draw.line([x2, y2, x2 - length*(dx*math.cos(angle) - dy*math.sin(angle)), 
                   y2 - length*(dy*math.cos(angle) + dx*math.sin(angle))], fill=color, width=3)

# Title
draw.text((width//2 - 400, 30), "Academix.io - Technical Architecture", fill=white, font=title_font)
draw.text((width//2 - 350, 90), "Academic Automation Platform with AI Agents", fill=gray, font=heading_font)

y_offset = 180

# Frontend Section
draw.text((100, y_offset), "FRONTEND (Vercel)", fill=purple, font=heading_font)
y_offset += 50
frontend_boxes = [
    (150, y_offset, 300, 80, "Next.js 16 UI\nTailwind + Framer Motion"),
    (500, y_offset, 250, 80, "Dashboard\nParticle Background"),
    (800, y_offset, 250, 80, "Report Studio\nLab Reports"),
    (1100, y_offset, 250, 80, "Transcription Hub\nYouTube/Audio"),
    (1400, y_offset, 250, 80, "Settings\nAPI Keys"),
    (1700, y_offset, 250, 80, "History\nChat Logs"),
]
for x, y, w, h, text in frontend_boxes:
    draw_box(x, y, w, h, purple, text, small_font)

y_offset += 120

# Backend Section
draw.text((100, y_offset), "BACKEND (Railway - FastAPI)", fill=blue, font=heading_font)
y_offset += 50
draw_box(150, y_offset, 400, 80, blue, "FastAPI Server\nPort 8080\nCORS Enabled", text_font)
draw_box(600, y_offset, 400, 80, blue, "CrewAI Orchestrator\nMulti-Agent System", text_font)
draw_box(1050, y_offset, 400, 80, blue, "SQLite Database\nChat History & Notes", text_font)

y_offset += 120

# AI Agents Section
draw.text((100, y_offset), "AI AGENTS (CrewAI)", fill=green, font=heading_font)
y_offset += 50
agent_boxes = [
    (150, y_offset, 280, 70, "Planner Agent\nWorkflow Router"),
    (470, y_offset, 280, 70, "YouTube Assistant\nTranscription"),
    (790, y_offset, 280, 70, "Coder Agent\nCode Execution"),
    (150, y_offset+100, 280, 70, "Lab Report Gen\nAcademic Reports"),
    (470, y_offset+100, 280, 70, "Numerical Methods\nMATLAB/Octave"),
    (790, y_offset+100, 280, 70, "Elite Writer\nDoctoral-Level Docs"),
]
for x, y, w, h, text in agent_boxes:
    draw_box(x, y, w, h, green, text, small_font)

y_offset += 220

# Bot Bypass System (NEW)
draw.text((1150, y_offset - 220), "BOT BYPASS SYSTEM (NEW)", fill=pink, font=heading_font)
bypass_y = y_offset - 170
bypass_boxes = [
    (1150, bypass_y, 280, 60, "User Agent Rotator\n6 Browser Agents"),
    (1470, bypass_y, 280, 60, "Retry Handler\nExp. Backoff 2s→32s"),
    (1150, bypass_y+80, 280, 60, "Cookie Manager\nOptional Auth"),
    (1470, bypass_y+80, 280, 60, "Error Classifier\nSmart Handling"),
]
for x, y, w, h, text in bypass_boxes:
    draw_box(x, y, w, h, pink, text, small_font)

# Tools Section
draw.text((100, y_offset), "TOOLS & SERVICES", fill=orange, font=heading_font)
y_offset += 50
tool_boxes = [
    (150, y_offset, 250, 60, "YouTube Downloader\n+ Bot Bypass"),
    (430, y_offset, 250, 60, "Faster Whisper\nTranscription"),
    (710, y_offset, 250, 60, "Code Compiler\nPython Execution"),
    (990, y_offset, 250, 60, "Data Viz Tool\nCharts & Graphs"),
    (150, y_offset+80, 250, 60, "Web Search\nSerper API"),
    (430, y_offset+80, 250, 60, "Citation Finder\nIEEE Format"),
    (710, y_offset+80, 250, 60, "PDF Parser\nAdobe API"),
    (990, y_offset+80, 250, 60, "Notion Integration\nNote Storage"),
    (150, y_offset+160, 250, 60, "Wolfram Alpha\nMath Solver"),
    (430, y_offset+160, 250, 60, "Octave Online\nMATLAB Execution"),
    (710, y_offset+160, 250, 60, "Grammar Checker\nProofreading"),
    (990, y_offset+160, 250, 60, "FFmpeg\nAudio Processing"),
]
for x, y, w, h, text in tool_boxes:
    draw_box(x, y, w, h, orange, text, small_font)

y_offset += 260

# External APIs Section
draw.text((100, y_offset), "EXTERNAL APIs", fill=red, font=heading_font)
y_offset += 50
api_boxes = [
    (150, y_offset, 250, 60, "OpenAI API\nGPT-4o-mini"),
    (430, y_offset, 250, 60, "Groq API\nLlama 3 70B"),
    (710, y_offset, 250, 60, "Serper API\nWeb Search"),
    (990, y_offset, 250, 60, "Notion API\nNote Storage"),
    (1270, y_offset, 250, 60, "Adobe PDF API\nPDF Extraction"),
    (150, y_offset+80, 250, 60, "Wolfram API\nComputations"),
    (430, y_offset+80, 250, 60, "Octave API\nCode Execution"),
    (710, y_offset+80, 250, 60, "YouTube\nyt-dlp"),
]
for x, y, w, h, text in api_boxes:
    draw_box(x, y, w, h, red, text, small_font)

y_offset += 180

# Key Features
draw.text((100, y_offset), "KEY FEATURES", fill=white, font=heading_font)
y_offset += 50
features = [
    "✓ Multi-Agent AI System with CrewAI orchestration",
    "✓ YouTube Bot Bypass with user agent rotation & retry logic",
    "✓ Parallel transcription with 4 worker threads",
    "✓ Doctoral-level academic report generation",
    "✓ Code execution with Python, MATLAB, Octave",
    "✓ Real-time web search and citation finding",
    "✓ Client-side API key storage (no server storage)",
    "✓ Deployed on Vercel (frontend) + Railway (backend)",
]
for i, feature in enumerate(features):
    draw.text((150, y_offset + i*35), feature, fill=white, font=text_font)

y_offset += 320

# Footer
draw.text((width//2 - 300, y_offset), "Built by Muhammad Saad bin Mazhar", fill=gray, font=heading_font)
draw.text((width//2 - 200, y_offset + 40), "Version 2.0.0 - 2025", fill=gray, font=text_font)

# Draw some connecting arrows
# Frontend to Backend
draw_arrow(400, 350, 400, 470, purple)
# Backend to Agents
draw_arrow(800, 550, 500, 670, blue)
# Agents to Tools
draw_arrow(500, 870, 500, 1090, green)
# Tools to External APIs
draw_arrow(600, 1350, 600, 1470, orange)
# Bot Bypass to YouTube
draw_arrow(1400, bypass_y+140, 850, 1550, pink)

# Save
output_path = os.path.join(os.path.dirname(__file__), 'academix_architecture.png')
img.save(output_path, 'PNG', quality=95)
print(f"Architecture diagram saved to: {output_path}")
