import os
from src.gemini_api_wrapper import GeminiAPIWrapper
from src.prompts import NOTE_GENERATION_PROMPT

class NoteGenerationService:
    @staticmethod
    def generate(transcript_path: str, output_path: str, prompt_text: str = None) -> bool:
        """
        Generates notes from a transcript file.
        Saves the notes to output_path.
        """
        if not os.path.exists(transcript_path):
            print(f"      ❌ Transcript file not found: {transcript_path}")
            return False

        if prompt_text is None:
            prompt_text = NOTE_GENERATION_PROMPT

        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                transcript_content = f.read()
            
            full_prompt = f"{prompt_text}\n\nTRANSCRIPT:\n{transcript_content}"
            
            api = GeminiAPIWrapper()
            notes = api.generate_content(full_prompt, model_type="note")
            
            if notes:
                out_dir = os.path.dirname(output_path)
                if out_dir and not os.path.exists(out_dir):
                    os.makedirs(out_dir, exist_ok=True)
                    
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(notes)
                
                return True
            else:
                print("      ⚠️ Warning: No notes extracted.")
                return False
        except Exception as e:
            print(f"      ❌ Note generation failed: {str(e)}")
            return False