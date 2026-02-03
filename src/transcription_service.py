import os
from typing import List
from src.gemini_api_wrapper import GeminiAPIWrapper
from src.prompts import TRANSCRIPTION_PROMPT

class TranscriptionService:
    @staticmethod
    def transcribe_chunks(chunks: List[str], output_file: str) -> bool:
        """
        Transcribes a list of audio chunks and appends text to output_file.
        Returns True if at least some transcription was successful.
        """
        out_dir = os.path.dirname(output_file)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        if os.path.exists(output_file):
            os.remove(output_file)

        api = GeminiAPIWrapper()
        any_success = False
        for i, chunk in enumerate(chunks):
            print(f"      - Processing chunk {i+1}/{len(chunks)}...")
            
            try:
                text = api.generate_content_with_file(
                    file_path=chunk,
                    prompt=TRANSCRIPTION_PROMPT,
                    model_type="transcription"
                )
                
                if text:
                    with open(output_file, 'a', encoding='utf-8') as f:
                        f.write(text)
                        f.write("\n\n") # Double newline between chunks
                    any_success = True
                else:
                    print(f"      ⚠️ Warning: No text extracted from chunk {i+1}")
                    return False
            except Exception as e:
                print(f"      ❌ Failed to get transcription for chunk {i+1}: {str(e)}")
                return False # Fail-fast on error
                
        return any_success