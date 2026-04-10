from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import os
import time
from typing import Any

import requests
import socketio


class OctaveOnlineInput(BaseModel):
    """Input schema for OctaveOnlineTool."""
    code: str = Field(..., description="Octave/MATLAB code to execute")
    timeout: int = Field(30, description="Execution timeout in seconds (default: 30)")


def execute_octave_code(code: str, timeout: int = 30) -> dict:
    """Execute Octave code via a configurable HTTP endpoint and return results."""
    try:
        configured_endpoint = os.getenv("OCTAVE_EXEC_ENDPOINT", "").strip()
        endpoint_candidates = [
            configured_endpoint,
            "https://octave-online.net/api/v0/evaluate",
            "https://octave-online.net/api/evaluate",
            "https://octave-online.net/evaluate",
        ]
        endpoints = [url for url in endpoint_candidates if url]

        payload = {
            "code": code,
            "timeout": timeout,
        }

        headers = {
            "Content-Type": "application/json",
        }

        last_error = "No endpoint attempted"
        for url in endpoints:
            response = requests.post(url, json=payload, headers=headers, timeout=timeout + 10)

            if response.status_code != 200:
                last_error = f"{url} -> HTTP {response.status_code}: {response.text[:500]}"
                continue

            try:
                result = response.json()
            except ValueError:
                last_error = f"{url} -> Non-JSON response: {response.text[:500]}"
                continue

            return {
                "success": True,
                "output": result.get("output", ""),
                "error": result.get("error", ""),
                "status": f"Execution completed via {url}",
                "endpoint": url,
            }

        # If REST is unavailable, fallback to Socket.IO (Octave Online native transport).
        socket_result = _execute_octave_code_socketio(code=code, timeout=timeout)
        if socket_result["success"]:
            return socket_result

        return {
            "success": False,
            "output": "",
            "error": (
                "No reachable Octave execution REST endpoint was found. "
                "Tried Socket.IO fallback as well. "
                "Set OCTAVE_EXEC_ENDPOINT in .env to a valid HTTP execution API if you have one. "
                f"Last REST error: {last_error}. Socket error: {socket_result.get('error', '')}"
            ),
            "status": "Execution failed",
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "output": "",
            "error": "Request timed out. Code took too long to execute.",
            "status": "Timeout",
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "output": "",
            "error": "Could not connect to Octave Online. Check your internet connection.",
            "status": "Connection error",
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "status": "Error",
        }


def _extract_socket_text(payload: Any) -> str:
    if payload is None:
        return ""
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        text = payload.get("data") or payload.get("output") or payload.get("message")
        return text if isinstance(text, str) else str(payload)
    if isinstance(payload, list):
        parts = [_extract_socket_text(item) for item in payload]
        return "".join(parts)
    return str(payload)


def _execute_octave_code_socketio(code: str, timeout: int) -> dict:
    socket_url = os.getenv("OCTAVE_SOCKET_URL", "https://octave-online.net").strip()
    socket_path = os.getenv("OCTAVE_SOCKET_PATH", "v2-socket.io").strip()

    chunks: list[str] = []
    last_data_time = 0.0
    connected = False
    command_sent = False
    error_message = ""

    sio = socketio.Client(reconnection=False, logger=False, engineio_logger=False)

    class _CaptureNamespace(socketio.ClientNamespace):
        def trigger_event(self, event: str, *args: Any) -> Any:
            nonlocal last_data_time, command_sent
            if event in {"data", "prompt"}:
                payload = args[0] if args else None

                text = ""
                if event == "data":
                    if isinstance(payload, dict):
                        data_text = payload.get("data")
                        if isinstance(data_text, str):
                            text = data_text
                    elif isinstance(payload, str):
                        text = payload
                elif event == "prompt" and isinstance(payload, dict):
                    prompt_text = payload.get("prompt")
                    if isinstance(prompt_text, str):
                        text = prompt_text

                if text:
                    chunks.append(text)
                    last_data_time = time.time()

                # Send command only after prompt/session is ready.
                ready_text = _extract_socket_text(payload)
                if not command_sent and ("octave:" in ready_text or "sessCode" in ready_text):
                    sio.emit("data", {"data": code})
                    command_sent = True
            return super().trigger_event(event, *args)

    sio.register_namespace(_CaptureNamespace("/"))

    @sio.event
    def connect() -> None:
        nonlocal connected
        connected = True
        # Matches the browser workflow where an init event is sent after connect.
        sio.emit("init", {"action": "session", "sessCode": "", "skipCreate": False})

    @sio.event
    def connect_error(data: Any) -> None:
        nonlocal error_message
        error_message = f"connect_error: {data}"

    @sio.event
    def error(data: Any) -> None:
        nonlocal error_message
        error_message = f"socket_error: {data}"

    @sio.on("data")
    def on_data(data: Any) -> None:
        nonlocal last_data_time
        text = _extract_socket_text(data)
        if text:
            chunks.append(text)
            last_data_time = time.time()

    @sio.event
    def disconnect() -> None:
        return None

    try:
        sio.connect(
            socket_url,
            socketio_path=socket_path,
            transports=["websocket", "polling"],
            headers={"Origin": "https://octave-online.net"},
        )

        deadline = time.time() + max(timeout, 5)
        while time.time() < deadline:
            sio.sleep(0.2)
            if chunks and (time.time() - last_data_time) > 1.4:
                break

        output = "".join(chunks).strip()
        if output:
            return {
                "success": True,
                "output": output,
                "error": "",
                "status": "Execution completed via Socket.IO",
                "endpoint": f"{socket_url.rstrip('/')}/{socket_path.lstrip('/')}",
            }

        if not connected and not error_message:
            error_message = "Could not establish Socket.IO connection."
        elif connected and not error_message:
            error_message = "Connected, but no output received before timeout."

        return {
            "success": False,
            "output": "",
            "error": error_message,
            "status": "Socket.IO execution failed",
        }
    except Exception as exc:
        return {
            "success": False,
            "output": "",
            "error": str(exc),
            "status": "Socket.IO execution error",
        }
    finally:
        try:
            if sio.connected:
                sio.disconnect()
        except Exception:
            pass


def format_lab_report(
    code: str,
    output: str,
    title: str = "Numerical Methods Lab Report",
    explanation: str = "",
) -> str:
    """Format Octave execution results into a lab report."""
    report = f"""# {title}

## Objective
Execute numerical methods algorithms and analyze results.

## Implementation

### Octave Code
```octave
{code}
```

## Output
```
{output}
```

"""

    if explanation:
        report += f"""## Analysis & Explanation
{explanation}

"""

    report += """## Conclusion
The above code demonstrates numerical methods implementation with actual computed results.
"""

    return report


class OctaveOnlineTool(BaseTool):
    name: str = "OctaveOnline"
    description: str = (
        "Executes Octave/MATLAB code using either a configurable HTTP API endpoint "
        "or Octave Online Socket.IO transport. "
        "Configure OCTAVE_EXEC_ENDPOINT for REST or OCTAVE_SOCKET_URL/OCTAVE_SOCKET_PATH for socket mode. "
        "Perfect for numerical methods lab manuals, matrix operations, solving equations, "
        "integration, differential equations, and other computational tasks. "
        "Returns both code and output for report generation."
    )
    args_schema: type[BaseModel] = OctaveOnlineInput

    def _run(self, code: str, timeout: int = 30) -> str:
        """Execute Octave code and return results."""
        if not code or not code.strip():
            return "Error: No code provided. Please provide valid Octave/MATLAB code to execute."

        result = execute_octave_code(code, timeout)

        if result["success"]:
            output_text = result.get("output", "")
            if result.get("error"):
                output_text += f"\n\n[Warning]: {result['error']}"

            return output_text
        else:
            error_msg = result.get("error", "Unknown error")
            return f"Execution failed: {error_msg}"
