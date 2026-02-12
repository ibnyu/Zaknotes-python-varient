import os
import shutil
import subprocess
import base64
from typing import List

class AudioProcessor:
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Returns the file size in bytes."""
        if not os.path.exists(file_path):
            return 0
        return os.path.getsize(file_path)

    @staticmethod
    def is_under_limit(file_path: str, limit_mb: int = 15) -> bool:
        """Checks if the file size is under the specified limit in MB."""
        size_bytes = AudioProcessor.get_file_size(file_path)
        limit_bytes = limit_mb * 1024 * 1024
        return size_bytes < limit_bytes

    @staticmethod
    def encode_to_base64(file_path: str) -> str:
        """Encodes a file to a base64 string."""
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    @staticmethod
    def get_duration(file_path: str) -> float:
        """Returns the duration of the audio file in seconds."""
        try:
            command = [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", file_path
            ]
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            val = result.stdout.strip()
            return float(val) if val and val != "N/A" else 0.0
        except (subprocess.CalledProcessError, ValueError):
            return 0.0

    @staticmethod
    def get_bitrate(file_path: str) -> int:
        """Returns the bitrate in bits per second."""
        try:
            command = [
                "ffprobe", "-v", "error", "-select_streams", "a:0",
                "-show_entries", "stream=bit_rate", "-of", "default=noprint_wrappers=1:nokey=1",
                file_path
            ]
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            val = result.stdout.strip()
            if val == "N/A" or not val:
                command = [
                    "ffprobe", "-v", "error", "-show_entries", "format=bit_rate", 
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    file_path
                ]
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                val = result.stdout.strip()
            
            return int(val) if val and val != "N/A" else 0
        except (subprocess.CalledProcessError, ValueError):
            return 0

    @staticmethod
    def reencode_to_optimal(input_path: str, output_path: str, bitrate: str = "48k", threads: int = 0) -> bool:
        """Re-encodes the audio to an optimal bitrate for transcription."""
        try:
            print(f"      - Re-encoding {input_path} at {bitrate} (optimal, threads={threads})...")
            command = [
                "ffmpeg", "-y", "-threads", str(threads), "-i", input_path,
                "-b:a", bitrate,
                "-ac", "1", # Mono is usually better for transcription and smaller size
                "-ar", "16000", # 16kHz is standard for many speech models
                output_path
            ]
            subprocess.run(command, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"      ❌ Error during optimal re-encoding: {e.stderr.decode('utf-8', errors='replace')}")
            return False

    @staticmethod
    def remove_silence(input_path: str, output_path: str, threshold_db: int = -50, threads: int = 0) -> bool:
        """Removes silence from the audio using ffmpeg silenceremove filter."""
        try:
            print(f"      - Removing silence (threshold: {threshold_db}dB, threads={threads})...")
            command = [
                "ffmpeg", "-y", "-threads", str(threads), "-i", input_path,
                "-af", f"silenceremove=stop_periods=-1:stop_duration=1:stop_threshold={threshold_db}dB",
                output_path
            ]
            subprocess.run(command, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"      ❌ Error during silence removal: {e.stderr.decode('utf-8', errors='replace')}")
            return False

    @staticmethod
    def split_into_chunks(input_path: str, output_pattern: str, segment_time: int = 1800, threads: int = 0) -> List[str]:
        """
        Splits the audio into chunks of specified duration (default 1800s / 30m).
        Returns a list of paths to the created chunks.
        """
        try:
            print(f"      - Splitting into chunks of {segment_time}s (threads={threads})...")
            command = [
                "ffmpeg", "-y", "-threads", str(threads), "-i", input_path,
                "-f", "segment",
                "-segment_time", str(segment_time),
                "-c", "copy",
                output_pattern
            ]
            subprocess.run(command, check=True, capture_output=True)
            
            directory = os.path.dirname(output_pattern) or "."
            base_parts = os.path.basename(output_pattern).split("%")
            prefix = base_parts[0]
            
            chunks = []
            for f in sorted(os.listdir(directory)):
                if f.startswith(prefix) and f != os.path.basename(input_path):
                     chunks.append(os.path.join(directory, f))
            return chunks
            
        except subprocess.CalledProcessError as e:
            print(f"      ❌ Error during splitting: {e.stderr.decode('utf-8', errors='replace')}")
            return []

    @staticmethod
    def split_by_size(input_path: str, output_pattern: str, max_size_mb: int = 15, threads: int = 0) -> List[str]:
        """
        Splits the audio into chunks of specified maximum size in MB.
        """
        try:
            current_size_bytes = AudioProcessor.get_file_size(input_path)
            target_size_bytes = max_size_mb * 1024 * 1024
            
            if current_size_bytes <= target_size_bytes:
                # No splitting needed, but copy to match pattern-ish if needed or just return single
                directory = os.path.dirname(output_pattern) or "."
                base_name = os.path.basename(output_pattern).replace("%03d", "001")
                single_chunk = os.path.join(directory, base_name)
                shutil.copy2(input_path, single_chunk)
                return [single_chunk]

            duration = AudioProcessor.get_duration(input_path)
            if duration <= 0:
                return []
            
            # Estimate segment time: (target_size / current_size) * total_duration
            # We add a 10% safety margin to ensure we are under the MB limit
            segment_time = int((target_size_bytes / current_size_bytes) * duration * 0.9)
            if segment_time < 10: segment_time = 10 # Minimum 10s
            
            print(f"      - Splitting into chunks based on size (estimated segment: {segment_time}s, threads={threads})...")
            return AudioProcessor.split_into_chunks(input_path, output_pattern, segment_time, threads=threads)
            
        except Exception as e:
            print(f"      ❌ Error during size-based splitting: {e}")
            return []

    @staticmethod
    def process_for_transcription(input_path: str, max_size_mb: int = 15, output_dir: str = "temp", threads: int = 0, output_pattern: str = None) -> List[str]:
        """
        Orchestrates the audio processing using duration-based chunking.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # 1. First, always remove silence and re-encode to optimal bitrate
        print(f"   - Preparing audio for transcription...")
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        extension = os.path.splitext(input_path)[1] or ".mp3"
        
        prepared_path = os.path.join(output_dir, f"{base_name}_prepared{extension}")
        
        # Intermediate path for silence removal
        silence_removed_path = prepared_path + ".nosilence" + extension
        if AudioProcessor.remove_silence(input_path, silence_removed_path, threads=threads):
            if not AudioProcessor.reencode_to_optimal(silence_removed_path, prepared_path, threads=threads):
                # If re-encoding fails, use silence removed version
                shutil.copy2(silence_removed_path, prepared_path)
            try: os.remove(silence_removed_path)
            except: pass
        else:
            # If silence removal fails, try re-encoding original
            if not AudioProcessor.reencode_to_optimal(input_path, prepared_path, threads=threads):
                # If both fail, use original
                shutil.copy2(input_path, prepared_path)

        # 2. Check size and split if needed
        if AudioProcessor.is_under_limit(prepared_path, max_size_mb):
            print(f"   - Processed file size is within limit ({max_size_mb} MB).")
            # Copy to match pattern for consistency if needed, but here we can just return it
            # To be consistent with split_by_size return, let's copy it
            if not output_pattern:
                output_pattern = os.path.join(output_dir, f"{base_name}_chunk_%03d{extension}")
            
            directory = os.path.dirname(output_pattern) or "."
            final_path = os.path.join(directory, os.path.basename(output_pattern).replace("%03d", "001"))
            shutil.copy2(prepared_path, final_path)
            return [final_path]

        print(f"   - Processed file size exceeds limit ({max_size_mb} MB). Splitting...")
        if not output_pattern:
            output_pattern = os.path.join(output_dir, f"{base_name}_chunk_%03d{extension}")
        
        chunks = AudioProcessor.split_by_size(prepared_path, output_pattern, max_size_mb, threads=threads)
        print(f"   - Split into {len(chunks)} chunks.")
        
        return chunks
