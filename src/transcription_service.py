import json
import os
from typing import List
from src.gemini_wrapper import GeminiCLIWrapper
from src.prompts import TRANSCRIPTION_PROMPT

class TranscriptionService:
    @staticmethod
    def transcribe_chunks(chunks: List[str], model: str, output_file: str) -> bool:
        """
        Transcribes a list of audio chunks and appends text to output_file.
        Returns True if all chunks succeeded, False otherwise.
        """
        out_dir = os.path.dirname(output_file)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        if os.path.exists(output_file):
            os.remove(output_file)

        for i, chunk in enumerate(chunks):
            print(f"      - Processing chunk {i+1}/{len(chunks)}...")
            prompt = TRANSCRIPTION_PROMPT.format(chunk=chunk)
            args = [
                "-m", model,
                "--output-format", "json",
                prompt
            ]
            
            result = GeminiCLIWrapper.run_command(args)
            
            if not result['success']:
                print(f"      ❌ Gemini CLI failed for chunk {i+1}: {result.get('stderr')}")
                return False
                
            try:
                stdout_str = result['stdout']
                if not stdout_str:
                    print(f"      ❌ Empty stdout for chunk {i+1}")
                    return False
                
                # Check for truncation
                if len(stdout_str) >= 65535:
                    print(f"      ⚠️ Warning: Output for chunk {i+1} is {len(stdout_str)} bytes. It might be truncated.")

                data = json.loads(stdout_str)
                text = data.get("response", "")
                if text:
                    with open(output_file, 'a', encoding='utf-8') as f:
                        f.write(text)
                        f.write("\n") # Add newline between chunks
                else:
                    print(f"      ⚠️ Warning: No 'response' key in JSON for chunk {i+1}")
            except json.JSONDecodeError as e:
                print(f"      ❌ JSON Decode Error for chunk {i+1}: {e}")
                # Log a bit of the stdout to help debug
                preview = stdout_str[:100] + "..." + stdout_str[-100:] if len(stdout_str) > 200 else stdout_str
                print(f"      - Output Preview: {preview}")
                return False
                
        return True
