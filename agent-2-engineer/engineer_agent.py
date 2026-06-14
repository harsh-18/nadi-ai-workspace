import os
import requests
import json 
import time
import hashlib 
from dotenv import load_dotenv

load_dotenv()

FEATHERLESS_API_KEY = os.getenv("FEATHERLESS_API_KEY")


BAND_API_KEY = os.getenv("BAND_API_KEY")
BAND_ROOM_ID = os.getenv("BAND_ROOM_ID")

FEATHERLESS_URL = "https://api.featherless.ai/v1/chat/completions"
# Centralized model config — change this ONE line to hot-swap models
# (e.g., switch to Llama) if Mistral gives poor results
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"


# NOTE: Provisional Band SDK endpoint structure.
# Pending confirmation against the official Band SDK documentation —
# to be finalized once the room integration spec is shared by the team.
BAND_BASE_URL = "https://api.bandprotocol.com/rooms"
BAND_LISTEN_URL = f"{BAND_BASE_URL}/{BAND_ROOM_ID}/messages/latest"
BAND_PUBLISH_URL = f"{BAND_BASE_URL}/{BAND_ROOM_ID}/messages"

# How often (in seconds) we check the Band room for new error reports
POLL_INTERVAL_SEC = 5

 
def build_prompt(error_report: dict)-> str:
    # .get() prevents crashes if the field is missing from the JSON
    error_type = error_report.get("error_type", "UnknownError")
    error_message = error_report.get("error_message", "No message provided")
    stack_trace = error_report.get("stack_trace", "No stack trace available")
    file_path = error_report.get("file_path", "unknown file")
    line_number = error_report.get("line_number", "?")
    language = error_report.get("language", "Python")

    prompt = f"""You are an expert {language} backend engineer.
A production server has crashed. Below is the exact error report captured by our monitoring system.
 
ERROR TYPE    : {error_type}
ERROR MESSAGE : {error_message}
FILE          : {file_path}  (line {line_number})
 
STACK TRACE:
{stack_trace}
 
YOUR TASK:
1. Diagnose the root cause of the error.
2. Write a minimal, production-safe {language} code patch that fixes the issue.
3. Include a brief comment above the fix explaining what you changed and why.
4. Return ONLY the corrected code block — no markdown, no explanations outside the code.
 
Begin the patch now:"""
    
    return prompt



def call_featherless(prompt: str)-> str:
    if not FEATHERLESS_API_KEY:
        raise EnvironmentError(
            "FEATHERLESS_API_KEY is not set. Add it to your .env file"
        )
    
    headers = {
        "Authorization": f"Bearer {FEATHERLESS_API_KEY}",
        "Content-Type": 'application/json',
    }


    payload = {
        "model": MODEL_NAME,
        "messages":[
            {
                "role": "system",
                "content":(
                    "You are an autonomous patch engineer. "
                    "You receive structured error reports and respond ONLY with code. "
                    "Do not include markdown fences or prose - pure code only."
                ),
            },
            {"role":"user", "content": prompt}
        ],
        "max_tokens":1024,
        "temperature":0.2,# Low temperature = more deterministic, focused patches (less "creative" randomness)
    }

    try:
        response = requests.post(FEATHERLESS_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()

        data = response.json()
        # extract the generated code text from Featherless's response
        patch_code = data["choices"][0]["message"]["content"].strip()
        return patch_code
    except Exception as e:
        print(f"[Featherless API Error] {e}")
        raise


def band_headers() -> dict:
    if not BAND_API_KEY:
        raise EnvironmentError("BAND_API_KEY is not set. Add it to your .env file.")
    return{
         # Bearer token tells the Band room who we are and authorizes the request
        "Authorization": f"Bearer {BAND_API_KEY}",
        "Content-Type": "application/json"
    }


def listen_for_sentry_report() -> dict | None:
    try:
        response = requests.get(
            BAND_LISTEN_URL,
            headers=band_headers(),
            timeout=10,
        )
        response.raise_for_status()
        message = response.json()

        # Only act on messages tagged as coming from the Sentry agent —
        # ignore any other message types in the room
        if message.get("type") == "sentry_report":
            print(f"[Sentry Report Recieved] {json.dumps(message, indent=2)}")
            return message.get("payload", {})
        
    except requests.exceptions.RequestException as exc:
        print(f"[Band Listen Error] {exc}")

    return None


def publish_patch_to_band(error_report: dict, patch_code: str) -> bool:
    outbound = {
        "type": "engineer_patch",
        "agent": "Agent-2-PatchEngineer",
        "model_used": MODEL_NAME,
        "original_error":{
            "error_type": error_report.get("error_type"),
            "error_message": error_report.get("error_message"),
            "file_path": error_report.get("file_path"),
            "line_number": error_report.get("line_number")
        },
        "patch": patch_code,
        "status": "AWAITING_REVIEW",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    try:
        response = requests.post(
            BAND_PUBLISH_URL,
            headers=band_headers(),
            json=outbound,
            timeout=10
        )
       # Stop immediately if the Band room returns an error (4xx/5xx)
        response.raise_for_status()
        print(f"[Patch Published] Sent to Band room -> {BAND_PUBLISH_URL}")
        return True
    
    except requests.exceptions.RequestException as exc:
        print(f"[Band Publish Error] {exc}")
        return False
    

HARDCODED_TEST_REPORT = {
    "error_type": "KeyError",
    "error_message": "'user_id'",
    "file_path": "api/handlers/auth.py",
    "line_number": 42,
    "language": "Python",
    "stack_trace": (
        "Traceback (most recent call last):\n"
        "  File 'api/handlers/auth.py', line 42, in authenticate\n"
        "   uid = request_data['user_id']\n"
        "KeyError: 'user_id'"
    ),
}


def run_smoke_test():
    print("=" * 60)
    print("  NADI AI — Agent 2: Smoke Test (no Band room)")
    print("=" * 60)
    print("\n[Input] Hardcoded error report:")
    print(json.dumps(HARDCODED_TEST_REPORT, indent=2))
 
    prompt = build_prompt(HARDCODED_TEST_REPORT)
    print("\n[Featherless] Sending prompt …")
    
    try:
        patch = call_featherless(prompt)
        print("\n[Generated Patch]")
        print("-" * 40)
        print(patch)
        print("-" * 40)
        print("\n Smoke Test passed. Featherless API is working")
    except Exception as exc:
        print(f"\n Smoke test failed: {exc}")

    
def main():
    print("=" * 60)
    print("  NADI AI — Agent 2: The Patch Engineer (LIVE MODE)")
    print(f"  Listening on Band Room: {BAND_ROOM_ID}")
    print(f"  Model: {MODEL_NAME}")
    print("=" * 60)


    # Keep track of error reports we've already patched,
    # so we don't generate duplicate patches for the same crash
    processed_reports = set()

    # Run forever — this agent stays alive and keeps checking for new errors
    while True:
        print(f"\n[Poll] Checking Band room ... ({time.strftime('%H:%M:%S')})")

        error_report = listen_for_sentry_report()

        if error_report:
            # Convert error report into a hash so we don't process the same error twice
            report_id = hashlib.sha256(
                json.dumps(error_report, sort_keys=True).encode()
            ).hexdigest()

            if report_id in processed_reports:
                print("[Skip] Already processed this report. Waiting for a new one. ")
            else:
                print("\n[Step 1/3] Building prompt... ")
                prompt = build_prompt(error_report)

                print("[Step 2/3] Calling featherless AI for patch generation ...")
                try:
                    patch_code = call_featherless(prompt)
                    print(f"[Patch Generated]\n{patch_code[:300]} ...")

                    print("[Step 3/3] Publishing patch to band room ...")
                    success = publish_patch_to_band(error_report, patch_code)

                    if success:
                        processed_reports.add(report_id)
                        print("Patch Delivered to Reviewer agent. Waiting for next error ...")
                    else:
                        print("Patch Delivered but failed to publish. Check band SDK credentials")

                except Exception as exc:
                    print(f"patch generatin failed: {exc}")

        else:
            print("[Idle] No new Sentry report. Will check again shortly. ")

        time.sleep(POLL_INTERVAL_SEC)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_smoke_test()
    else:
        main()