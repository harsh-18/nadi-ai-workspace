"""sentry_parser.py
Parse raw system logs into a structured ``ErrorReport`` using LangChain and the
Qwen2.5‑Coder model. The output is a Pydantic model that matches the hand‑off
schema used across the multi‑agent pipeline.
"""

import os
import logging
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# LangChain core imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Initialise logging – keep it concise and machine friendly
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("sentry_parser")

# Load environment variables from .env
load_dotenv()

# ---------------------------------------------------------------------
# 1. Contract – Pydantic schema for deterministic hand‑off
# ---------------------------------------------------------------------
class ErrorReport(BaseModel):
    error_type: str = Field(
        description="Exception class or error identifier (e.g., ConnectionTimeoutError, ZeroDivisionError)"
    )
    severity: str = Field(
        description="Severity level – one of: LOW, MEDIUM, HIGH, CRITICAL"
    )
    file_path: Optional[str] = Field(
        default=None,
        description="File path where the error originated; null if not identifiable"
    )
    line_number: Optional[int] = Field(
        default=None,
        description="Line number of the failure; null if not identifiable"
    )
    error_message: str = Field(
        description="Short, human‑readable summary of the error message"
    )
    stack_trace: str = Field(
        description="Relevant traceback or raw log excerpt that provides context"
    )

# ---------------------------------------------------------------------
# 2. Parser implementation
# ---------------------------------------------------------------------
class SentryParser:
    """Core parsing engine for Agent 1.

    It sends the raw log to the Qwen2.5‑Coder model via LangChain, requesting a
    JSON output that conforms to :class:`ErrorReport`. Errors are caught and a
    safe fallback ``ErrorReport`` is returned so the runtime never crashes.
    """

    def __init__(self) -> None:
        # Prefer FEATHERLESS_API_KEY, then fallback to OPENAI_API_KEY
        self.api_key = os.getenv("FEATHERLESS_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv(
            "OPENAI_API_BASE", "https://api.featherless.ai/v1"
        )
        self.model_name = os.getenv(
            "LLM_MODEL_NAME", "Qwen/Qwen2.5-Coder-32B-Instruct"
        )
        if not self.api_key:
            raise ValueError("Missing API key for LLM – set FEATHERLESS_API_KEY or OPENAI_API_KEY in .env")

        logger.info("Initialising Qwen‑Coder LLM: %s", self.model_name)
        self.llm = ChatOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            model=self.model_name,
            temperature=0.0,
        )
        # Bind the structured output to our Pydantic model
        self.structured_llm = self.llm.with_structured_output(ErrorReport)

    def parse_log(self, raw_log: str) -> ErrorReport:
        """Parse *raw_log* and return a validated :class:`ErrorReport`.

        An empty or whitespace‑only log triggers a deterministic fallback report.
        """
        if not raw_log or not raw_log.strip():
            logger.warning("Empty log supplied – returning fallback report")
            return self._fallback_report("Empty log input")

        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are an automated diagnostics agent (The Sentry). "
                "Extract the error details from the provided log and output a JSON object "
                "that matches the ErrorReport schema exactly.",
            ),
            ("human", "Log input:\n\n{raw_log}"),
        ])
        chain = prompt | self.structured_llm
        try:
            logger.info("Invoking LLM for log analysis")
            report = chain.invoke({"raw_log": raw_log})
            logger.info("LLM parsing succeeded")
            return report
        except Exception as exc:  # pragma: no cover
            logger.error("LLM invocation failed: %s", exc)
            return self._fallback_report(str(exc), raw_log)

    def _fallback_report(self, reason: str, raw_log: str = "") -> ErrorReport:
        """Create a safe ``ErrorReport`` when parsing cannot be performed."""
        return ErrorReport(
            error_type="ParsingException",
            severity="MEDIUM",
            file_path=None,
            line_number=None,
            error_message=f"Failed to parse log – {reason}",
            stack_trace=raw_log,
        )

# Simple manual test entry point
if __name__ == "__main__":
    sample = """
    2026-06-12 15:04:15 [ERROR] Worker crashed:\nTraceback (most recent call last):\n  File \"/app/main.py\", line 10, in <module>\n    run()\nZeroDivisionError: division by zero\n    """
    parser = SentryParser()
    result = parser.parse_log(sample)
    print(result.model_dump_json(indent=2))
