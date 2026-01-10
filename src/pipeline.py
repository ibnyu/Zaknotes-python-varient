import os
from src.downloader import download_audio
from src.audio_processor import AudioProcessor
from src.transcription_service import TranscriptionService
from src.note_generation_service import NoteGenerationService
from src.pdf_converter_py import PdfConverter
from src.cleanup_service import FileCleanupService

class ProcessingPipeline:
    def __init__(self, config_manager):
        self.config = config_manager
        self.pdf_converter = PdfConverter()

    def execute_job(self, job) -> bool:
        """
        Executes the full pipeline for a single job.
        """
        audio_path = None
        chunks = []
        transcript_path = None
        notes_path = None
        html_path = None
        
        try:
            # 1. Download
            job['status'] = 'downloading'
            audio_path = download_audio(job)
            if not audio_path or not os.path.exists(audio_path):
                print(f"❌ Download failed or file missing for job: {job['name']}")
                job['status'] = 'failed'
                return False

            # 2. Audio Processing
            job['status'] = 'processing'
            temp_dir = "temp"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir, exist_ok=True)
                
            chunks = AudioProcessor.process_for_transcription(
                audio_path, 
                limit_mb=20, 
                output_dir=temp_dir
            )
            
            # 3. Transcription
            transcript_path = os.path.join(temp_dir, f"{job['id']}_transcript.txt")
            t_model = self.config.get("transcription_model")
            if not TranscriptionService.transcribe_chunks(chunks, t_model, transcript_path):
                print(f"❌ Transcription failed for job: {job['name']}")
                job['status'] = 'failed'
                return False

            # 4. Note Generation
            notes_path = os.path.join(temp_dir, f"{job['id']}_notes.md")
            n_model = self.config.get("note_generation_model")
            if not NoteGenerationService.generate(transcript_path, n_model, notes_path):
                print(f"❌ Note generation failed for job: {job['name']}")
                job['status'] = 'failed'
                return False

            # 5. PDF Conversion
            safe_name = job['name'].replace(" ", "_").replace("/", "-")
            if not os.path.exists("pdfs"):
                os.makedirs("pdfs", exist_ok=True)
                
            final_pdf_path = os.path.join("pdfs", f"{safe_name}.pdf")
            html_path = os.path.join(temp_dir, f"{job['id']}_temp.html")
            
            self.pdf_converter.convert_md_to_html(notes_path, html_path)
            self.pdf_converter.convert_html_to_pdf(html_path, final_pdf_path)
            
            # 6. Cleanup
            files_to_cleanup = [audio_path, transcript_path, notes_path, html_path]
            for c in chunks:
                if c != audio_path:
                    files_to_cleanup.append(c)
            FileCleanupService.cleanup_job_files(files_to_cleanup)
            
            job['status'] = 'completed'
            print(f"✅ Job '{job['name']}' completed successfully. PDF: {final_pdf_path}")
            return True

        except Exception as e:
            print(f"❌ Exception in pipeline for job {job['id']}: {e}")
            job['status'] = 'failed'
            # Cleanup whatever we can on failure? 
            # User says: "make sure after prossesing each link there should be only the pdf left"
            # This implies even on failure we should probably clean up chunks/audio.
            files_to_cleanup = [audio_path, transcript_path, notes_path, html_path]
            for c in chunks:
                if c != audio_path:
                    files_to_cleanup.append(c)
            FileCleanupService.cleanup_job_files(files_to_cleanup)
            return False