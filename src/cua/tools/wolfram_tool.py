import os
import urllib.parse
import requests
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class WolframAlphaInput(BaseModel):
    """Input schema for WolframAlphaTool."""
    query: str = Field(..., description="The query to ask Wolfram Alpha (e.g., 'integral of x^2', 'distance to the moon').")


class WolframAlphaTool(BaseTool):
    name: str = "WolframAlphaTool"
    description: str = (
        "Queries the Wolfram Alpha computational intelligence engine. "
        "Useful for calculating complex mathematical expressions, fetching physical constants, "
        "or retrieving scientific facts. Returns a concise text result."
    )
    args_schema: type[BaseModel] = WolframAlphaInput

    def _run(self, query: str) -> str:
        app_id = os.getenv("WOLFRAM_ALPHA_APPID", "").strip()
        if not app_id:
            return "Error: WOLFRAM_ALPHA_APPID environment variable is missing. Cannot query Wolfram Alpha."

        try:
            # Short answers API
            url = f"http://api.wolframalpha.com/v1/result?appid={app_id}&i={urllib.parse.quote(query)}"
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                return response.text
            elif response.status_code == 501:
                return f"Wolfram Alpha could not provide a short answer for: '{query}'."
            elif response.status_code == 403:
                return "Error: Invalid Wolfram Alpha API key (HTTP 403)."
            else:
                return f"Wolfram Alpha API error: HTTP {response.status_code}. Response: {response.text[:100]}"
                
        except requests.exceptions.Timeout:
            return "Error: Request to Wolfram Alpha timed out."
        except requests.exceptions.RequestException as e:
            return f"Error connecting to Wolfram Alpha: {str(e)}"
