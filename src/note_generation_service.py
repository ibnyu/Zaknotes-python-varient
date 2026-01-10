import json
import os
from src.gemini_wrapper import GeminiCLIWrapper
from src.prompts import NOTE_GENERATION_PROMPT

class NoteGenerationService:
    @staticmethod
    def generate(transcript_path: str, model: str, output_path: str, prompt_text: str = None) -> bool:
        """
        Generates notes from a transcript file using the specified model and prompt text.
        Saves the notes to output_path.
        """
        if not os.path.exists(transcript_path):
            print(f"      ❌ Transcript file not found: {transcript_path}")
            return False

        if prompt_text is None:
            prompt_text = NOTE_GENERATION_PROMPT

        # Replace placeholder with file reference format for CLI
        prompt = prompt_text.replace("@transcription/file/location", f"@{transcript_path}")
        
        args = [
            "-m", model,
            "--output-format", "json",
            prompt
        ]
        
        result = GeminiCLIWrapper.run_command(args)
        
        if not result['success']:
            print(f"      ❌ Gemini CLI failed: {result.get('stderr')}")
            return False
            
        try:
            stdout_str = result['stdout']
            data = json.loads(stdout_str)
            notes = data.get("response", "")
            if notes:
                out_dir = os.path.dirname(output_path)
                if out_dir and not os.path.exists(out_dir):
                    os.makedirs(out_dir, exist_ok=True)
                    
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(notes)
                return True
            else:
                print("      ⚠️ Warning: No 'response' key in JSON for notes")
                return False
        except json.JSONDecodeError as e:
            print(f"      ❌ JSON Decode Error for notes: {e}")
            return False
