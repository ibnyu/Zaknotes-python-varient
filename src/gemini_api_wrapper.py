import time
import httpx
import logging
import json
import os
from typing import Optional, List, Dict, Any
from src.gemini_auth_service import GeminiAuthService, GeminiCliAuthRecord
from src.usage_tracker import UsageTracker
from src.audio_processor import AudioProcessor

logger = logging.getLogger(__name__)

class GeminiAPIWrapper:
    CODE_ASSIST_ENDPOINT = "https://cloudcode-pa.googleapis.com"
    GEMINI_CLI_HEADERS = {
        "User-Agent": "google-cloud-sdk vscode_cloudshelleditor/0.1",
        "X-Goog-Api-Client": "gl-node/22.17.0",
        "Client-Metadata": json.dumps({
            "ideType": "IDE_UNSPECIFIED",
            "platform": "PLATFORM_UNSPECIFIED",
            "pluginType": "GEMINI",
        }),
    }

    def __init__(self, config=None, auth_service=None, usage_tracker=None):
        from src.config_manager import ConfigManager
        self.config = config or ConfigManager()
        self.auth_service = auth_service or GeminiAuthService()
        self.usage_tracker = usage_tracker or UsageTracker()
        
        self.api_timeout = self.config.get("api_timeout", 300)
        self.api_max_retries = self.config.get("api_max_retries", 3)
        self.api_retry_delay = self.config.get("api_retry_delay", 10)
        
        self.error_file = "error.json"

    def _log_error(self, request_body: Any, response_data: Any):
        """Logs the full request and response to error.json."""
        error_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "request": request_body,
            "response": response_data
        }
        
        errors = []
        if os.path.exists(self.error_file):
            try:
                with open(self.error_file, 'r') as f:
                    errors = json.load(f)
                    if not isinstance(errors, list):
                        errors = []
            except Exception:
                errors = []
        
        errors.append(error_entry)
        # Keep last 50 errors to avoid massive file
        errors = errors[-50:]
        
        with open(self.error_file, 'w') as f:
            json.dump(errors, f, indent=4)

    async def generate_content_async(self, prompt: str, audio_base64: Optional[str] = None, model_type: str = "note") -> str:
        model_name = self.config.get(f"{model_type}_model") or "gemini-2.0-flash"
        
        while True:
            auth_record = self.auth_service.get_next_account()
            if not auth_record:
                raise Exception("No Gemini CLI accounts configured. Please add an account first.")
            
            # Ensure token is valid
            try:
                auth_record = await self.auth_service.get_valid_account(auth_record)
            except Exception as e:
                logger.error(f"Failed to refresh token for {auth_record.get('email')}: {e}")
                continue # Try next account

            # Prepare parts
            parts = []
            if audio_base64:
                parts.append({"inline_data": {"mime_type": "audio/mp3", "data": audio_base64}})
            parts.append({"text": prompt})

            request_id = f"pi-{int(time.time()*1000)}-{os.urandom(4).hex()}"
            request_body = {
                "project": auth_record["projectId"],
                "model": model_name,
                "request": {
                    "contents": [
                        {
                            "role": "user",
                            "parts": parts,
                        },
                    ],
                },
                "userAgent": "pi-cli-standalone",
                "requestId": request_id,
            }

            for attempt in range(self.api_max_retries + 1):
                logger.info(f"Gemini API Request - Account: {auth_record['email']}, Type: {model_type}, Model: {model_name} (Attempt: {attempt + 1})")
                
                start_time = time.time()
                try:
                    async with httpx.AsyncClient(timeout=self.api_timeout) as client:
                        resp = await client.post(
                            f"{self.CODE_ASSIST_ENDPOINT}/v1internal:streamGenerateContent?alt=sse",
                            headers={
                                "Authorization": f"Bearer {auth_record['access']}",
                                "Content-Type": "application/json",
                                "Accept": "text/event-stream",
                                **self.GEMINI_CLI_HEADERS,
                            },
                            json=request_body
                        )

                        if resp.status_code != 200:
                            error_payload = resp.text
                            try:
                                error_payload = resp.json()
                            except: pass
                            
                            self._log_error(request_body, error_payload)
                            logger.error(f"Gemini API Error ({resp.status_code}) for {auth_record['email']}")
                            
                            if resp.status_code in [401, 403, 429]:
                                # 429 is exhaustion, 401/403 might be expired or permission issues
                                break # Move to next account
                            
                            if resp.status_code == 503:
                                logger.warning("Service Unavailable (503). Retrying...")
                                time.sleep(self.api_retry_delay)
                                continue
                            
                            raise Exception(f"API Error {resp.status_code}: {resp.text}")

                        # Process SSE stream
                        full_text = ""
                        for line in resp.iter_lines():
                            if line.startswith("data:"):
                                json_str = line[5:].strip()
                                if not json_str: continue
                                try:
                                    chunk = json.loads(json_str)
                                    candidates = chunk.get("response", {}).get("candidates", [])
                                    if candidates:
                                        parts_resp = candidates[0].get("content", {}).get("parts", [])
                                        for p in parts_resp:
                                            if "text" in p:
                                                full_text += p["text"]
                                except Exception:
                                    continue

                        duration = time.time() - start_time
                        logger.info(f"Gemini API Response - Success - Duration: {duration:.2f}s")
                        
                        # Record usage
                        self.usage_tracker.record_usage(auth_record["email"] or "unknown", model_name)
                        return full_text

                except httpx.TimeoutException:
                    logger.warning(f"Gemini API Timeout (Attempt {attempt+1})")
                    if attempt >= self.api_max_retries:
                        break # Try next account
                    time.sleep(self.api_retry_delay)
                except Exception as e:
                    logger.error(f"Gemini API Exception: {e}")
                    self._log_error(request_body, str(e))
                    if attempt >= self.api_max_retries:
                        break # Try next account
                    time.sleep(self.api_retry_delay)

    # Synchronous wrappers for existing pipeline
    def generate_content(self, prompt, model_type="note", system_instruction=None):
        import asyncio
        # Combine system instruction and prompt for v1internal as it doesn't explicitly 
        # separate them in the same way in the streamGenerateContent body (usually)
        # based on gemini.ts. Actually, we can put them in parts.
        full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
        return asyncio.run(self.generate_content_async(full_prompt, model_type=model_type))

    def generate_content_with_file(self, file_path, prompt, model_type="transcription", system_instruction=None):
        import asyncio
        audio_base64 = AudioProcessor.encode_to_base64(file_path)
        full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
        return asyncio.run(self.generate_content_async(full_prompt, audio_base64=audio_base64, model_type=model_type))

    def _wait_for_file_active(self, client, file_obj):
        """Waits for the uploaded file to be in ACTIVE state."""
        while file_obj.state == "PROCESSING":
            time.sleep(2)
            file_obj = client.files.get(name=file_obj.name)
        
        if file_obj.state != "ACTIVE":
            raise Exception(f"File {file_obj.name} failed to process with state {file_obj.state}")
