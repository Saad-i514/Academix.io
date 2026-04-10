"""
Web Search Tool - Uses SerperDev API for internet searches.
This tool is kept as a wrapper for easy integration and future customization.
"""

from crewai_tools import SerperDevTool

# Initialize the search tool
search_tool = SerperDevTool()

__all__ = ["search_tool"]
