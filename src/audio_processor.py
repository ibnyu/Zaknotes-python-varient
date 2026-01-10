import os
import subprocess
from typing import List

class AudioProcessor:
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Returns the file size in bytes."""
        if not os.path.exists(file_path):
            return 0
        return os.path.getsize(file_path)

    @staticmethod
    def is_under_limit(file_path: str, limit_mb: int = 20) -> bool:
        """Checks if the file size is under the specified limit in MB."""
        size_bytes = AudioProcessor.get_file_size(file_path)
        limit_bytes = limit_mb * 1024 * 1024
        return size_bytes < limit_bytes

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
                 # Try format bitrate if stream bitrate is N/A
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
    def reencode_audio(input_path: str, output_path: str, bitrate: str = "16k") -> bool:
        """Re-encodes the audio to a lower bitrate using ffmpeg."""
        try:
            command = [
                "ffmpeg", "-y", "-i", input_path,
                "-b:a", bitrate,
                output_path
            ]
            subprocess.run(command, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error during re-encoding: {e.stderr.decode()}")
            return False

    @staticmethod
    def split_into_chunks(input_path: str, output_pattern: str, segment_time: int = 1800) -> List[str]:
        """
        Splits the audio into chunks of specified duration (default 1800s / 30m).
        Returns a list of paths to the created chunks.
        """
        try:
            command = [
                "ffmpeg", "-y", "-i", input_path,
                "-f", "segment",
                "-segment_time", str(segment_time),
                "-c", "copy",
                output_pattern
            ]
            subprocess.run(command, check=True, capture_output=True)
            
            # Find the created files
            directory = os.path.dirname(output_pattern) or "."
            base_parts = os.path.basename(output_pattern).split("%")
            prefix = base_parts[0]
            
            chunks = []
            for f in sorted(os.listdir(directory)):
                if f.startswith(prefix) and f != os.path.basename(input_path):
                     chunks.append(os.path.join(directory, f))
            return chunks
            
        except subprocess.CalledProcessError as e:
            print(f"Error during splitting: {e.stderr.decode()}")
            return []

    @staticmethod
    def process_for_transcription(input_path: str, limit_mb: int = 20, segment_time: int = 1800, output_dir: str = "temp") -> List[str]:
        """
        Orchestrates the audio processing:
        1. Check size. If < limit, return [input_path].
        2. Else, split into chunks.
        3. For each chunk, iteratively reduce bitrate by 10kbps until < limit or min bitrate reached.
        4. Return list of chunk paths.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        if AudioProcessor.is_under_limit(input_path, limit_mb):
            return [input_path]

        # Needs splitting
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        extension = os.path.splitext(input_path)[1] or ".mp3"
        output_pattern = os.path.join(output_dir, f"{base_name}_chunk_%03d{extension}")
        
        chunks = AudioProcessor.split_into_chunks(input_path, output_pattern, segment_time)
        
        final_chunks = []
        for chunk in chunks:
            # Iteratively reduce bitrate if needed
            while not AudioProcessor.is_under_limit(chunk, limit_mb):
                current_bitrate = AudioProcessor.get_bitrate(chunk)
                if current_bitrate == 0:
                    current_bitrate = 128000 # Fallback default
                
                # Reduce by 10kbps (10,000 bps)
                new_bitrate_val = current_bitrate - 10000
                
                # Minimum floor: 32kbps
                if new_bitrate_val < 32000:
                    print(f"Warning: Chunk {chunk} is still too large ({AudioProcessor.get_file_size(chunk)} bytes) but bitrate is low ({current_bitrate}). Skipping further reduction.")
                    break
                
                reencoded_path = chunk + ".tmp" + extension
                if AudioProcessor.reencode_audio(chunk, reencoded_path, bitrate=str(new_bitrate_val)):
                    try:
                        os.remove(chunk)
                        os.rename(reencoded_path, chunk)
                    except OSError:
                        pass
                else:
                    break # Re-encode failed
            
            final_chunks.append(chunk)
                    
        return final_chunks