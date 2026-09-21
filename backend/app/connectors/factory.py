from app.connectors.base import BaseConnector
from app.connectors.http_connector import HttpConnector
from app.connectors.llm_connector import LlmConnector


def build_connector(connector_type: str, config: dict) -> BaseConnector:
    if connector_type == "http":
        return HttpConnector(config)
    if connector_type == "llm":
        return LlmConnector(config)
    raise ValueError(f"Unknown connector type: {connector_type}")
