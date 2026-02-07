import os
import time
from src.downloader import download_audio, get_expected_audio_path
from src.audio_processor import AudioProcessor
from src.note_generation_service import NoteGenerationService
from src.cleanup_service import FileCleanupService
from src.gemini_api_wrapper import GeminiAPIWrapper
from src.prompts import TRANSCRIPTION_PROMPT
from src.job_manager import JobManager

class ProcessingPipeline:
    def __init__(self, config_manager, api_wrapper=None, job_manager=None):
        self.config = config_manager
        self.manager = job_manager or JobManager()
        self.api = api_wrapper or GeminiAPIWrapper()

    def execute_job(self, job) -> bool:
        """
        Executes the full pipeline for a single job with resumption support.
        """
        self.api.key_manager.reset_quotas_if_needed()
        
        audio_path = None
        chunks = []
        transcript_path = None
        notes_path = None
        
        temp_dir = "temp"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir, exist_ok=True)

        try:
            # 1. Download (Skip if status >= DOWNLOADED or file exists)
            audio_path = get_expected_audio_path(job)
            skip_download = False
            if job.get('status') in ['DOWNLOADED', 'SILENCE_REMOVED', 'BITRATE_MODIFIED', 'CHUNKED'] or job.get('status', '').startswith('TRANSCRIBING_CHUNK_'):
                if os.path.exists(audio_path):
                    print(f"⏩ Skipping download: {audio_path} already exists.")
                    skip_download = True
            elif os.path.exists(audio_path):
                # Even if status is not set, if file exists we might want to skip or at least be aware
                print(f"⏩ Audio file {audio_path} already exists. Skipping download and setting status to DOWNLOADED.")
                job['status'] = 'DOWNLOADED' # Update in-memory object
                self.manager.update_job_status(job['id'], 'DOWNLOADED')
                skip_download = True
            
            if not skip_download:
                print(f"📥 [1/4] Downloading audio for: {job['name']}...")
                self.manager.update_job_status(job['id'], 'downloading')
                audio_path = download_audio(job)
                if not audio_path or not os.path.exists(audio_path):
                    print(f"❌ Download failed or file missing for job: {job['name']}")
                    self.manager.update_job_status(job['id'], 'failed')
                    return False
                self.manager.update_job_status(job['id'], 'DOWNLOADED')
                job['status'] = 'DOWNLOADED'

            # 2. Audio Processing (Skip if status >= CHUNKED)
            skip_processing = False
            if job.get('status') in ['CHUNKED'] or job.get('status', '').startswith('TRANSCRIBING_CHUNK_'):
                # Try to find existing chunks using job ID
                chunks = sorted([os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.startswith(f"job_{job['id']}_chunk_")])
                if chunks:
                    print(f"⏩ Skipping audio processing: {len(chunks)} chunk(s) found in {temp_dir}.")
                    skip_processing = True
            
            if not skip_processing:
                print(f"✂️ [2/4] Checking size and splitting audio: {audio_path}")
                self.manager.update_job_status(job['id'], 'processing')
                
                segment_time = self.config.get("segment_time", 1800)
                profile = self.config.get("performance_profile", "balanced")
                threads = 0
                if profile == "low": threads = 1
                elif profile == "high": threads = 0
                
                # We'll use a specific pattern including job ID
                extension = os.path.splitext(audio_path)[1] or ".mp3"
                output_pattern = os.path.join(temp_dir, f"job_{job['id']}_chunk_%03d{extension}")
                    
                chunks = AudioProcessor.process_for_transcription(
                    audio_path, 
                    segment_time=segment_time,
                    output_dir=temp_dir,
                    threads=threads,
                    output_pattern=output_pattern # Pass custom pattern
                )
                print(f"   - Audio split into {len(chunks)} chunk(s).")
                self.manager.update_job_status(job['id'], 'CHUNKED')
                job['status'] = 'CHUNKED'
            
            # 3. Transcription
            print(f"📝 [3/4] Transcribing {len(chunks)} chunks using Gemini...")
            transcript_path = os.path.join(temp_dir, f"{job['id']}_transcript.txt")
            
            # Implementation of 10s wait before chunks
            out_dir = os.path.dirname(transcript_path)
            if out_dir and not os.path.exists(out_dir):
                os.makedirs(out_dir, exist_ok=True)

            if os.path.exists(transcript_path) and job.get('status') == 'CHUNKED':
                 # If we are just starting transcription but file exists, clear it
                 os.remove(transcript_path)

            any_success = False
            # Get existing transcriptions if any
            existing_transcriptions = job.get('transcriptions', {})
            
            # Reconstruct transcript file from existing ones if resuming
            if existing_transcriptions:
                with open(transcript_path, 'w', encoding='utf-8') as f:
                    # Sort by chunk index
                    for idx in sorted(existing_transcriptions.keys(), key=int):
                        f.write(existing_transcriptions[idx])
                        f.write("\n\n")
                any_success = True
            elif not os.path.exists(transcript_path):
                # Ensure file exists for 'a' mode later if we have no existing trans
                with open(transcript_path, 'w', encoding='utf-8') as f:
                    pass

            for i, chunk in enumerate(chunks):
                chunk_index = i + 1
                if str(chunk_index) in existing_transcriptions:
                    print(f"      - Chunk {chunk_index}/{len(chunks)} already transcribed. Skipping.")
                    continue

                if any_success: # If we processed at least one chunk (resumed or new)
                    print(f"      - Waiting 10s before next chunk...")
                    time.sleep(10)
                
                print(f"      - Processing chunk {chunk_index}/{len(chunks)}...")
                self.manager.update_job_status(job['id'], f'TRANSCRIBING_CHUNK_{chunk_index}')
                try:
                    text = self.api.generate_content_with_file(
                        file_path=chunk,
                        prompt=TRANSCRIPTION_PROMPT,
                        model_type="transcription"
                    )
                    if text:
                        with open(transcript_path, 'a', encoding='utf-8') as f:
                            f.write(text)
                            f.write("\n\n")
                        self.manager.add_chunk_transcription(job['id'], chunk_index, text)
                        any_success = True
                    else:
                        print(f"      ⚠️ Warning: No text extracted from chunk {chunk_index}")
                        self.manager.update_job_status(job['id'], 'failed')
                        return False
                except Exception as e:
                    print(f"      ❌ Failed to get transcription for chunk {chunk_index}: {str(e)}")
                    self.manager.update_job_status(job['id'], 'failed')
                    return False

            if not any_success:
                print(f"❌ Transcription failed for job: {job['name']}")
                self.manager.update_job_status(job['id'], 'failed')
                return False
            print(f"   - Transcription complete: {transcript_path}")

            # 4. Note Generation
            print(f"🗒️ [4/4] Generating study notes...")
            safe_name = job['name'].replace(" ", "_").replace("/", "-")
            notes_dir = "notes"
            if not os.path.exists(notes_dir):
                os.makedirs(notes_dir, exist_ok=True)
            
            final_notes_path = os.path.join(notes_dir, f"{safe_name}.md")
            
            if not NoteGenerationService.generate(transcript_path, final_notes_path):
                print(f"❌ Note generation failed for job: {job['name']}")
                self.manager.update_job_status(job['id'], 'failed')
                return False
            print(f"   - Notes generated: {final_notes_path}")

            # 5. Cleanup
            print(f"🧹 Cleaning up intermediate files...")
            files_to_cleanup = [audio_path, transcript_path]
            for c in chunks:
                if c != audio_path:
                    files_to_cleanup.append(c)
            FileCleanupService.cleanup_job_files(files_to_cleanup)
            
            self.manager.update_job_status(job['id'], 'completed')
            print(f"✅ Job '{job['name']}' completed successfully! Notes: {final_notes_path}")
            return True

        except Exception as e:
            print(f"❌ Exception in pipeline for job {job['id']}: {e}")
            self.manager.update_job_status(job['id'], 'failed')
            return False
