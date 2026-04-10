"""
OctaveAPITool - Optional tool for Octave API authentication and validation.
This tool is kept for future use if users want to set up Octave API access.
Currently, the system uses OctaveOnlineTool which doesn't require API keys.
"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import os
import requests
from typing import Optional


class OctaveAPIInput(BaseModel):
    """Input schema for OctaveAPITool."""
    action: str = Field(..., description="Action to perform: 'validate', 'get_info', or 'test_connection'")
    api_key: Optional[str] = Field(None, description="Octave API key (optional, uses env var if not provided)")


def get_octave_api_key() -> str:
    """Retrieve Octave API key from environment."""
    api_key = os.getenv("OCTAVE_API_KEY", "").strip()
    if not api_key:
        raise ValueError("OCTAVE_API_KEY environment variable not set.")
    return api_key


def validate_octave_api_key(api_key: Optional[str] = None) -> dict:
    """Validate Octave API key format and connectivity."""
    if api_key is None:
        api_key = get_octave_api_key()

    if not api_key or len(api_key) < 10:
        return {
            "valid": False,
            "status": "Invalid format",
            "message": "API key is empty or too short",
        }

    return {
        "valid": True,
        "status": "Format valid",
        "message": "API key format appears valid",
        "key_length": len(api_key),
    }


def test_octave_connection(api_key: Optional[str] = None) -> dict:
    """Test connection to Octave API."""
    if api_key is None:
        api_key = get_octave_api_key()

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        response = requests.get(
            "https://api.octave.com/v1/account",
            headers=headers,
            timeout=10,
        )

        if response.status_code == 200:
            return {
                "connected": True,
                "status": "Connection successful",
                "message": "Successfully authenticated with Octave API",
            }
        elif response.status_code == 401:
            return {
                "connected": False,
                "status": "Authentication failed",
                "message": "API key is invalid or expired",
            }
        else:
            return {
                "connected": False,
                "status": f"HTTP {response.status_code}",
                "message": response.text[:200],
            }

    except requests.exceptions.ConnectionError:
        return {
            "connected": False,
            "status": "Connection error",
            "message": "Could not reach Octave API endpoint",
        }
    except requests.exceptions.Timeout:
        return {
            "connected": False,
            "status": "Timeout",
            "message": "Request to Octave API timed out",
        }
    except Exception as e:
        return {
            "connected": False,
            "status": "Error",
            "message": str(e),
        }


def get_octave_account_info(api_key: Optional[str] = None) -> dict:
    """Retrieve Octave account information."""
    if api_key is None:
        api_key = get_octave_api_key()

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        response = requests.get(
            "https://api.octave.com/v1/account",
            headers=headers,
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "account": data,
            }
        else:
            return {
                "success": False,
                "status": f"HTTP {response.status_code}",
                "message": "Failed to retrieve account information",
            }

    except Exception as e:
        return {
            "success": False,
            "status": "Error",
            "message": str(e),
        }


class OctaveAPITool(BaseTool):
    name: str = "OctaveAPITool"
    description: str = (
        "Manages Octave API authentication and key validation. "
        "Use this tool to validate API keys, test connections, and retrieve account information."
    )
    args_schema: type[BaseModel] = OctaveAPIInput

    def _run(self, action: str, api_key: Optional[str] = None) -> str:
        """Execute the specified Octave API action."""
        action = action.lower().strip()

        try:
            if action == "validate":
                result = validate_octave_api_key(api_key)
            elif action == "test_connection":
                result = test_octave_connection(api_key)
            elif action == "get_info":
                result = get_octave_account_info(api_key)
            else:
                return f"Unknown action: {action}. Supported actions: validate, test_connection, get_info"

            return str(result)

        except ValueError as e:
            return f"Configuration error: {str(e)}"
        except Exception as e:
            return f"Error executing {action}: {str(e)}"
