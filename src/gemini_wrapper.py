import subprocess
from typing import List, Dict, Any

class GeminiCLIWrapper:
    @staticmethod
    def run_command(args: List[str]) -> Dict[str, Any]:
        """
        Runs the gemini CLI with the provided arguments.
        Returns a dictionary with success status, stdout, and stderr.
        """
        if args and args[0] == "gemini":
            command = args
        else:
            command = ["gemini"] + args
        
        try:
            # We capture as bytes to handle potential encoding issues manually
            result = subprocess.run(
                command,
                capture_output=True,
                text=False,
                check=True
            )
            # Use utf-8 but replace errors to avoid crashing on truncated multibyte chars
            stdout = result.stdout.decode('utf-8', errors='replace')
            stderr = result.stderr.decode('utf-8', errors='replace')
            
            return {
                "success": True,
                "stdout": stdout,
                "stderr": stderr
            }
        except subprocess.CalledProcessError as e:
            stdout = e.stdout.decode('utf-8', errors='replace') if e.stdout else ""
            stderr = e.stderr.decode('utf-8', errors='replace') if e.stderr else str(e)
            return {
                "success": False,
                "stdout": stdout,
                "stderr": stderr
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e)
            }