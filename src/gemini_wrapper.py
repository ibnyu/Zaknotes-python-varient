import subprocess
from typing import List, Dict, Any

class GeminiCLIWrapper:
    @staticmethod
    def run_command(args: List[str]) -> Dict[str, Any]:
        """
        Runs the gemini CLI with the provided arguments.
        Returns a dictionary with success status, stdout, and stderr.
        """
        # Ensure we don't double-add 'gemini' if caller provided it, though test assumes we prepend
        if args and args[0] == "gemini":
            command = args
        else:
            command = ["gemini"] + args
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "stdout": e.stdout if hasattr(e, 'stdout') else "",
                "stderr": e.stderr if hasattr(e, 'stderr') else str(e)
            }
