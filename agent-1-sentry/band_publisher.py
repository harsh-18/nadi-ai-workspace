'''band_publisher.py
Implements routing of parsed AgentSpec data to the Band SDK.
Provides graceful fallback handling for timeouts and API errors.
'''\n\nfrom __future__ import annotations\n\nimport json\nimport logging\nfrom typing import Any, Dict\n\nimport httpx\n\n# Placeholder import for the Pydantic schema used by the parser\ntry:\n    from .agent_spec import AgentSpec  # type: ignore\nexcept Exception:  # pragma: no cover\n    from typing import TypedDict\n\n    class AgentSpec(TypedDict, total=False):\n        data: Dict[str, Any]\n\n# Configure a module‑level logger\nlogger = logging.getLogger(__name__)\n\n\nclass BandPublisher:\n    """Publish an ``AgentSpec`` to the Band service.
\n    The real Band SDK is assumed to expose an async ``publish`` method.
    This implementation uses ``httpx`` directly for simplicity and adds
    timeout handling and a deterministic fallback configuration.
    """
\n    def __init__(self, endpoint: str, timeout: float = 5.0) -> None:\n        self.endpoint = endpoint.rstrip('/')\n        self.timeout = timeout\n        self.client = httpx.Client(timeout=timeout)\n\n    def _build_payload(self, spec: AgentSpec) -> Dict[str, Any]:\n        """Convert the spec into the JSON payload expected by Band.
\n        If the spec is a Pydantic model it will be serialised via ``dict``;
        otherwise we fall back to a direct ``json`` dump.
        """
        if hasattr(spec, "model_dump"):\n            payload = spec.model_dump()  # type: ignore[attr-defined]\n        else:\n            payload = json.loads(json.dumps(spec))\n        return payload\n\n    def publish(self, spec: AgentSpec) -> bool:\n        """Publish *spec* to the Band endpoint.
\n        Returns ``True`` on success, ``False`` on any handled error.
        Network timeouts are caught and logged; a mock fallback payload is
        optionally sent if configured.
        """
        payload = self._build_payload(spec)\n        url = f"{self.endpoint}/publish"\n        try:\n            response = self.client.post(url, json=payload)\n            response.raise_for_status()\n            logger.info("Band publish succeeded", extra={"status_code": response.status_code})\n            return True\n        except httpx.TimeoutException as exc:\n            logger.error("Band publish timed out", exc_info=exc)\n            # Fallback: record the payload locally for later retry\n            try:\n                with open("band_fallback.json", "w", encoding="utf-8") as f:\n                    json.dump(payload, f, ensure_ascii=False, indent=2)\n                logger.info("Fallback payload written to band_fallback.json")\n            except Exception as fallback_exc:  # pragma: no cover\n                logger.error("Failed to write fallback payload", exc_info=fallback_exc)\n            return False\n        except httpx.HTTPError as exc:\n            logger.error("Band publish failed", exc_info=exc)\n            return False\n        finally:\n            # Ensure resources are released promptly\n            self.client.close()\n\n# Public API of the module\n__all__ = ["BandPublisher"]\n