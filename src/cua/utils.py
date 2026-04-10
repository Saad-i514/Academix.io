import streamlit as st
from crewai.project import CrewBase
from langchain_core.callbacks import BaseCallbackHandler
from typing import Any, Dict, List, Optional
import time

class StreamlitCallbackHandler(BaseCallbackHandler):
    """Custom callback handler to provide real-time updates in Streamlit."""
    
    def __init__(self, status_container):
        self.status_container = status_container
        self.current_step = ""

    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any) -> Any:
        pass

    def on_agent_action(self, action: Any, **kwargs: Any) -> Any:
        """Called when an agent takes an action."""
        tool = action.tool
        tool_input = action.tool_input
        log = action.log
        
        with self.status_container:
            st.markdown(f"**🤖 Agent Action:** Using tool `{tool}`")
            if tool_input:
                st.caption(f"Input: {tool_input}")
            # st.divider()

    def on_agent_finish(self, finish: Any, **kwargs: Any) -> Any:
        """Called when an agent finishes its task."""
        with self.status_container:
            st.success(f"✅ **Agent Finished!**")
            # st.markdown(f"> {finish.return_values.get('output', 'Task complete.')}")

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> Any:
        """Called when a tool starts."""
        pass

    def on_tool_end(self, output: str, **kwargs: Any) -> Any:
        """Called when a tool finishes."""
        with self.status_container:
            st.info(f"🛠️ **Tool Output (excerpt):** {output[:200]}...")

def inject_custom_css():
    """Inject premium CSS for glassmorphism and modern styling."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .main {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }

        div.stButton > button {
            background-color: #667eea;
            color: white;
            border-radius: 12px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            border: none;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        div.stButton > button:hover {
            background-color: #764ba2;
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }

        .glass-card {
            background: rgba(255, 255, 255, 0.25);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            backdrop-filter: blur(4px);
            -webkit-backdrop-filter: blur(4px);
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.18);
            padding: 20px;
            margin-bottom: 20px;
        }

        .stAlert {
            border-radius: 15px;
            border: none;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }

        h1, h2, h3 {
            color: #2d3436;
            font-weight: 700;
        }

        .sidebar .sidebar-content {
            background-image: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        /* Status Container styling */
        .status-box {
            border-left: 4px solid #667eea;
            padding-left: 15px;
            background: #fff;
            margin: 10px 0;
            border-radius: 8px;
        }

        .stChatMessage {
            background: rgba(255, 255, 255, 0.4);
            backdrop-filter: blur(8px);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 10px;
            margin-bottom: 10px;
        }

        .stTextInput > div > div > input {
            background: rgba(255, 255, 255, 0.6);
            border-radius: 10px;
            border: 1px solid #ddd;
        }

        .stTextArea > div > div > textarea {
            background: rgba(255, 255, 255, 0.6);
            border-radius: 10px;
            border: 1px solid #ddd;
        }

        /* Academic Report Styles */
        .report-container {
            background: white;
            padding: 40px;
            border-radius: 5px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border: 1px solid #eee;
            font-family: 'Inter', serif;
            line-height: 1.6;
            color: #2c3e50;
        }

        .report-container h1 {
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-size: 2.2rem;
        }

        .report-container h2 {
            border-bottom: 1px solid #eee;
            padding-bottom: 5px;
            margin-top: 30px;
            color: #764ba2;
        }

        .report-container blockquote {
            border-left: 5px solid #667eea;
            background: #f8f9fa;
            padding: 15px;
            font-style: italic;
            border-radius: 0 8px 8px 0;
        }

        .report-container table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }

        .report-container th {
            background: #f1f3f9;
            color: #2d3436;
            padding: 12px;
            text-align: left;
            border: 1px solid #dee2e6;
        }

        .report-container td {
            padding: 12px;
            border: 1px solid #dee2e6;
        }
        </style>
    """, unsafe_allow_html=True)

def render_glass_card(title, content):
    """Render a card with glassmorphism style."""
    st.markdown(f"""
    <div class="glass-card">
        <h3>{title}</h3>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)
