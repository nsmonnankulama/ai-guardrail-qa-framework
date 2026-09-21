import json
import time

import requests

from app.connectors.base import BaseConnector, ConnectorResponse


def _get_by_path(data, path: str):
    current = data
    for part in path.split("."):
        if part == "":
            continue
        if isinstance(current, list):
            current = current[int(part)]
        elif isinstance(current, dict):
            current = current.get(part)
        else:
            return None
        if current is None:
            return None
    return current


class HttpConnector(BaseConnector):
    def send(self, prompt: str, system_prompt: str = "") -> ConnectorResponse:
        url = self.config.get("url")
        method = self.config.get("method", "POST").upper()
        headers = self.config.get("headers") or {}
        request_template = self.config.get("request_template") or '{"message": "{{prompt}}"}'
        timeout = self.config.get("timeout", 30)

        body_str = request_template.replace("{{prompt}}", prompt.replace('"', '\\"'))
        try:
            payload = json.loads(body_str)
        except json.JSONDecodeError:
            payload = {"message": prompt}

        if self.config.get("response_mode") == "sse":
            return self._send_sse(url, method, headers, payload, timeout)
        return self._send_json(url, method, headers, payload, timeout)

    def _send_json(self, url, method, headers, payload, timeout) -> ConnectorResponse:
        response_path = self.config.get("response_path", "response")
        start = time.perf_counter()
        try:
            resp = requests.request(method, url, headers=headers, json=payload, timeout=timeout)
            latency_ms = (time.perf_counter() - start) * 1000
            resp.raise_for_status()
            data = resp.json()
            text = _get_by_path(data, response_path)
            if text is None:
                text = json.dumps(data)
            return ConnectorResponse(response_text=str(text), latency_ms=latency_ms, raw=data)
        except Exception as exc:
            latency_ms = (time.perf_counter() - start) * 1000
            return ConnectorResponse(response_text="", latency_ms=latency_ms, raw=None, error=str(exc))

    def _send_sse(self, url, method, headers, payload, timeout) -> ConnectorResponse:
        type_field = self.config.get("sse_type_field", "type")
        content_field = self.config.get("sse_content_field", "content")
        stream_types = self.config.get("sse_stream_types") or ["STREAM"]
        start = time.perf_counter()
        try:
            resp = requests.request(
                method, url, headers=headers, json=payload, timeout=timeout, stream=True
            )
            resp.raise_for_status()
            chunks = []
            events = []
            for raw_line in resp.iter_lines(decode_unicode=True):
                if not raw_line or not raw_line.startswith("data:"):
                    continue
                data_str = raw_line[len("data:"):].strip()
                try:
                    event = json.loads(data_str)
                except json.JSONDecodeError:
                    continue
                events.append(event)
                if event.get(type_field) in stream_types:
                    chunks.append(str(event.get(content_field, "")))
            latency_ms = (time.perf_counter() - start) * 1000
            return ConnectorResponse(response_text="".join(chunks), latency_ms=latency_ms, raw=events)
        except Exception as exc:
            latency_ms = (time.perf_counter() - start) * 1000
            return ConnectorResponse(response_text="", latency_ms=latency_ms, raw=None, error=str(exc))
