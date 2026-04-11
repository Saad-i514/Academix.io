from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import requests
import os
import re
from typing import Any

class NotionToolInput(BaseModel):
    """Input schema for NotionTool."""
    title: str = Field(..., description="Title for the Notion page.")
    notes: str = Field(..., description="Notes content to store in Notion.")
    subject: str = Field("General", description="Subject/category for the notes.")

 

def save_to_notion(title, notes, subject="General"):
    notion_api_key = os.getenv("NOTION_API_KEY", "").strip()
    raw_database_id = os.getenv("NOTION_DATABASE_ID", "").strip()
    title_property = os.getenv("NOTION_TITLE_PROPERTY", "Title").strip()
    subject_property = os.getenv("NOTION_SUBJECT_PROPERTY", "Subject").strip()
    notes_property = os.getenv("NOTION_NOTES_PROPERTY", "Notes").strip()

    # Make Notion optional - return friendly message if not configured
    if not notion_api_key or notion_api_key == "your_notion_api_key_here":
        return {
            "status": "skipped",
            "message": "Notion integration not configured. To enable, set NOTION_API_KEY in your .env file.",
            "id": None,
            "url": None
        }
    
    if not raw_database_id or raw_database_id == "your_notion_database_id_here":
        return {
            "status": "skipped",
            "message": "Notion database not configured. To enable, set NOTION_DATABASE_ID in your .env file.",
            "id": None,
            "url": None
        }

    database_id = _normalize_database_id(raw_database_id)

    url = "https://api.notion.com/v1/pages"

    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    schema = _get_database_schema(database_id, headers)
    properties: dict[str, Any] = {
        title_property: {
            "title": [
                {"text": {"content": title}}
            ]
        }
    }

    if subject_property in schema:
        subject_type = schema[subject_property].get("type", "")
        subject_value = _build_property_value(subject_type, subject)
        if subject_value is not None:
            properties[subject_property] = subject_value

    if notes_property in schema:
        notes_type = schema[notes_property].get("type", "")
        notes_value = _build_property_value(notes_type, notes)
        if notes_value is not None:
            properties[notes_property] = notes_value

    data = {
        "parent": {"database_id": database_id},
        "properties": properties,
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": notes[:2000]}}
                    ]
                }
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data, timeout=30)
    if not response.ok:
        raise RuntimeError(
            f"HTTP {response.status_code} from Notion API. "
            f"Body: {response.text}"
        )
    return response.json()


def _get_database_schema(database_id: str, headers: dict[str, str]) -> dict[str, Any]:
    response = requests.get(f"https://api.notion.com/v1/databases/{database_id}", headers=headers, timeout=30)
    if not response.ok:
        raise RuntimeError(
            f"HTTP {response.status_code} while reading database schema. "
            f"Body: {response.text}"
        )
    data = response.json()
    return data.get("properties", {})


def _build_property_value(property_type: str, value: str) -> dict[str, Any] | None:
    text_value = value[:2000]
    if property_type == "rich_text":
        return {"rich_text": [{"text": {"content": text_value}}]}
    if property_type == "title":
        return {"title": [{"text": {"content": text_value}}]}
    if property_type == "select":
        return {"select": {"name": text_value[:100]}}
    if property_type == "multi_select":
        return {"multi_select": [{"name": text_value[:100]}]}
    if property_type == "url":
        return {"url": text_value}
    return None


def _normalize_database_id(value: str) -> str:
    """Extract a 32-char Notion object ID from raw ID or full Notion URL."""
    match = re.search(r"([0-9a-fA-F]{32})", value)
    if not match:
        return value.strip()
    compact = match.group(1).lower()
    return f"{compact[0:8]}-{compact[8:12]}-{compact[12:16]}-{compact[16:20]}-{compact[20:32]}"


class NotionTool(BaseTool):
    name: str = "Notion"
    description: str = "Creates a new Notion page with the provided notes content."
    args_schema: type[BaseModel] = NotionToolInput

    def _run(self, title: str, notes: str, subject: str = "General") -> str:
        try:
            result = save_to_notion(title, notes, subject)
            
            # Handle optional Notion integration
            if isinstance(result, dict) and result.get("status") == "skipped":
                return f"Notion integration skipped: {result['message']}"
            
            page_id = result.get("id", "Unknown")
            page_url = result.get("url", "")
            return f"Notion page created with ID: {page_id}. URL: {page_url}"
        except Exception as e:
            return f"Notion upload failed: {e}. The app continues to work without Notion integration."
    