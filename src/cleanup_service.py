import os
import shutil

class FileCleanupService:
    @staticmethod
    def cleanup_job_files(files: list):
        """Deletes a list of files if they exist."""
        for f in files:
            if f and os.path.exists(f):
                try:
                    os.remove(f)
                    print(f"Cleanup: Deleted {f}")
                except Exception as e:
                    print(f"Cleanup: Failed to delete {f}: {e}")

    @staticmethod
    def cleanup_all_temp_files(temp_dir="temp", downloads_dir="downloads"):
        """
        Manually cleans up all intermediate files from temp and downloads.
        Keeps .gitkeep files.
        """
        # Cleanup temp
        if os.path.exists(temp_dir):
            for f in os.listdir(temp_dir):
                if f == ".gitkeep": continue
                path = os.path.join(temp_dir, f)
                try:
                    if os.path.isfile(path): os.remove(path)
                    elif os.path.isdir(path): shutil.rmtree(path)
                    print(f"Manual Cleanup: Deleted {path}")
                except Exception as e:
                    print(f"Manual Cleanup: Failed to delete {path}: {e}")

        # Cleanup downloads (only mp3/part files)
        if os.path.exists(downloads_dir):
            for f in os.listdir(downloads_dir):
                if f == ".gitkeep": continue
                # We only want to delete audio files and partial downloads
                if f.lower().endswith((".mp3", ".part", ".ytdl", ".m4a", ".webm")):
                    path = os.path.join(downloads_dir, f)
                    try:
                        os.remove(path)
                        print(f"Manual Cleanup: Deleted {path}")
                    except Exception as e:
                        print(f"Manual Cleanup: Failed to delete {path}: {e}")
