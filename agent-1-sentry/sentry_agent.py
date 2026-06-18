"""sentry_agent.py
Agent 1: The Sentry (Log Analyzer)
Role: Intercepts unstructured crash logs, parses them into a validated Pydantic model
using LangChain and Qwen2.5-Coder, and publishes the structured JSON payload to the
Band SDK room so Agent 2 (The Patch Engineer) can retrieve it.
"""

import os
import json
import logging
from typing import Optional, Dict, Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# LangChain imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Try importing the Band SDK, fallback to REST/Mock mode if not present
try:
    from band_sdk import BandClient
except ImportError:
    BandClient = None

# Configure logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SentryAgent")

# Load environment variables
load_dotenv()


# ---------------------------------------------------------------------
# STEP 1: Strict Pydantic Data Contract (Matches Agent 2 Expectations)
# ---------------------------------------------------------------------
class ErrorReport(BaseModel):
    error_type: str = Field(
        description="The class or type of error (e.g., KeyError, ValueError, OperationalError)"
    )
    severity: str = Field(
        description="Assigned severity of the incident: LOW, MEDIUM, HIGH, or CRITICAL"
    )
    file_path: Optional[str] = Field(
        default="unknown file",
        description="Relative or absolute path to the file where the execution failed"
    )
    line_number: Optional[int] = Field(
        default=None,
        description="The line number where the execution failed, or null if not identifiable"
    )
    error_message: str = Field(
        description="Concise description of the primary exception message"
    )
    stack_trace: str = Field(
        description="The relevant traceback section extracted from the raw log"
    )
    language: str = Field(
        default="Python",
        description="The programming language of the codebase (e.g., Python, Node.js)"
    )


# ---------------------------------------------------------------------
# STEP 2: Sentry Log Parser Engine
# ---------------------------------------------------------------------
class SentryParser:
    """Uses LangChain and Qwen2.5-Coder to extract structured details from raw logs."""
    
    def __init__(self) -> None:
        # Load API key and Base URL from either AI/ML API or Featherless AI configurations
        self.api_key = os.getenv("FEATHERLESS_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_API_BASE", "https://api.aimlapi.com/v1")
        self.model_name = os.getenv("LLM_MODEL_NAME", "Qwen/Qwen2.5-Coder-32B-Instruct")
        
        if not self.api_key:
            raise ValueError("No valid LLM API key detected. Please configure your .env file.")

        logger.info(f"Initializing parsing model: {self.model_name}")
        
        # Initialize LangChain LLM Client
        self.llm = ChatOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            model=self.model_name,
            temperature=0.0  # Greedy decoding for consistent, deterministic parsing
        )
        
        # Enforce Pydantic parsing matching our schema using json_mode for Featherless compatibility
        self.structured_llm = self.llm.with_structured_output(ErrorReport, method="json_mode")

    def parse_log(self, raw_log: str) -> ErrorReport:
        """Parses a raw crash log into a structured ErrorReport instance."""
        if not raw_log or not raw_log.strip():
            logger.warning("Empty log provided to the Sentry Agent. Generating fallback report.")
            return self._fallback_report("Empty trace log provided.")

        import json
        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an automated DevOps diagnostics agent (The Sentry). "
                "Analyze the provided log trace, isolate the core issue, and extract "
                "the details matching the requested JSON format exactly.\n\n"
                "Desired JSON Schema:\n{schema_json}"
            )),
            ("human", "Here is the raw error log:\n\n{raw_log}"),
        ])

        chain = prompt | self.structured_llm
        
        try:
            logger.info("Parsing log trace...")
            schema_json = json.dumps(ErrorReport.model_json_schema())
            report = chain.invoke({"raw_log": raw_log, "schema_json": schema_json})
            return report
        except Exception as exc:
            logger.error(f"Failed to parse log via LLM: {exc}")
            return self._fallback_report(str(exc), raw_log)

    def _fallback_report(self, reason: str, original_log: str = "") -> ErrorReport:
        """Generates a default schema-valid report to prevent system failures."""
        return ErrorReport(
            error_type="ParsingException",
            severity="MEDIUM",
            file_path="unknown file",
            line_number=None,
            error_message=f"Log parsing failed: {reason}",
            stack_trace=original_log,
            language="Python"
        )


# ---------------------------------------------------------------------
# STEP 3: Band Room Publisher (Configured for Agent 2 Integration)
# ---------------------------------------------------------------------
class BandRoomPublisher:
    """Interacts with the Band Room to publish Sentry reports."""
    
    def __init__(self) -> None:
        self.api_key = os.getenv("BAND_API_KEY")
        self.room_id = os.getenv("BAND_ROOM_ID")
        
        # Check if the real Band SDK is installed and configured
        if BandClient and self.api_key:
            self.client = BandClient(api_key=self.api_key)
            logger.info("Band SDK client successfully initialized.")
        else:
            self.client = None
            logger.warning("Band SDK not detected or BAND_API_KEY is missing. Operating in mock/CLI fallback mode.")

    def publish_report(self, report: ErrorReport) -> bool:
        """Publishes the report using the precise payload structure expected by Agent 2."""
        payload_data = report.model_dump()
        
        # CRITICAL: This structured envelope matches what Agent 2's listener reads
        outbound_envelope = {
            "type": "sentry_report",
            "payload": payload_data
        }
        
        print("\n--- [SENTRY OUTPUT ENVELOPE] ---")
        print(json.dumps(outbound_envelope, indent=2))
        print("--------------------------------\n")
        
        if self.client and self.room_id:
            try:
                # Dispatch payload using the Band SDK API client
                self.client.send_message(
                    room_id=self.room_id,
                    text="[Sentry Alert] Structured crash report generated.",
                    payload=outbound_envelope,
                )
                logger.info(f"Report successfully transmitted to Band Room: {self.room_id}")
                return True
            except Exception as exc:
                logger.error(f"Failed to publish to Band Room: {exc}")
                return False
        else:
            logger.info("Running in mock mode. Payload generated and output to console.")
            return True


# ---------------------------------------------------------------------
# STEP 4: Execution / Demonstration
# ---------------------------------------------------------------------
if __name__ == "__main__":
    # Test data: A simulated messy python traceback
    simulated_log = """
    2026-06-12 15:04:12 [WARNING] Connection pool size reached 90% capacity.
    2026-06-12 15:04:15 [ERROR] Worker-7 crashed unexpectedly:
    Traceback (most recent call last):
      File "/app/utils/db_connector.py", line 114, in query_database
        cursor.execute(sql_query)
    psycopg2.OperationalError: Connection closed unexpectedly by server.
    2026-06-12 15:04:16 [INFO] Worker-7 reboot process initiated.
    """
    
    try:
        parser = SentryParser()
        publisher = BandRoomPublisher()
        
        # 1. Parse the log
        report = parser.parse_log(simulated_log)
        
        # 2. Publish to Band Room
        publisher.publish_report(report)
        
    except Exception as e:
        logger.error(f"Execution failed: {e}")