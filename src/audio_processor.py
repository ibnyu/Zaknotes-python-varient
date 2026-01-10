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
            print(f"      - Re-encoding {input_path} at {bitrate}...")
            command = [
                "ffmpeg", "-y", "-i", input_path,
                "-b:a", bitrate,
                output_path
            ]
            subprocess.run(command, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"      ❌ Error during re-encoding: {e.stderr.decode('utf-8', errors='replace')}")
            return False

    @staticmethod
    def split_into_chunks(input_path: str, output_pattern: str, segment_time: int = 1800) -> List[str]:
        """
        Splits the audio into chunks of specified duration (default 1800s / 30m).
        Returns a list of paths to the created chunks.
        """
        try:
            print(f"      - Splitting into chunks of {segment_time}s...")
            command = [
                "ffmpeg", "-y", "-i", input_path,
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
    def process_for_transcription(input_path: str, limit_mb: int = 20, segment_time: int = 1800, output_dir: str = "temp") -> List[str]:
        """
        Orchestrates the audio processing.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        size_mb = AudioProcessor.get_file_size(input_path) / (1024 * 1024)
        if size_mb < limit_mb:
            print(f"   - File size ({size_mb:.2f}MB) is within limit ({limit_mb}MB).")
            return [input_path]

        print(f"   - File size ({size_mb:.2f}MB) exceeds limit. Splitting...")
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        extension = os.path.splitext(input_path)[1] or ".mp3"
        output_pattern = os.path.join(output_dir, f"{base_name}_chunk_%03d{extension}")
        
        chunks = AudioProcessor.split_into_chunks(input_path, output_pattern, segment_time)
        print(f"   - Split into {len(chunks)} chunks.")
        
        final_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_size_mb = AudioProcessor.get_file_size(chunk) / (1024 * 1024)
            print(f"   - Validating chunk {i+1}: {chunk} ({chunk_size_mb:.2f}MB)")
            
            while not AudioProcessor.is_under_limit(chunk, limit_mb):
                current_bitrate = AudioProcessor.get_bitrate(chunk)
                if current_bitrate == 0:
                    current_bitrate = 128000
                
                new_bitrate_val = current_bitrate - 10000
                if new_bitrate_val < 32000:
                    print(f"      ⚠️ Minimum bitrate reached. Proceeding with large chunk.")
                    break
                
                reencoded_path = chunk + ".tmp" + extension
                if AudioProcessor.reencode_audio(chunk, reencoded_path, bitrate=str(new_bitrate_val)):
                    try:
                        os.remove(chunk)
                        os.rename(reencoded_path, chunk)
                        new_size_mb = AudioProcessor.get_file_size(chunk) / (1024 * 1024)
                        print(f"      - Reduced bitrate to {new_bitrate_val/1000:.0f}k. New size: {new_size_mb:.2f}MB")
                    except OSError:
                        pass
                else:
                    break
            
            final_chunks.append(chunk)
                    
        return final_chunks
