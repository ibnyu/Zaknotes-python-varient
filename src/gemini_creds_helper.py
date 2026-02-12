import os
import re
import sys
import shutil
from pathlib import Path
from typing import Optional

def find_in_path(name: str) -> Optional[str]:
    return shutil.which(name)

def extract_gemini_cli_credentials():
    gemini_path = find_in_path("gemini")
    if not gemini_path:
        return None

    try:
        resolved_path = os.path.realpath(gemini_path)
        gemini_cli_dir = Path(resolved_path).parent.parent

        search_paths = [
            gemini_cli_dir / "node_modules" / "@google" / "gemini-cli-core" / "dist" / "src" / "code_assist" / "oauth2.js",
            gemini_cli_dir / "node_modules" / "@google" / "gemini-cli-core" / "dist" / "code_assist" / "oauth2.js",
        ]

        content = None
        for candidate in search_paths:
            if candidate.exists():
                content = candidate.read_text(encoding='utf-8')
                break

        if not content:
            # Fallback search
            for p in gemini_cli_dir.rglob("oauth2.js"):
                content = p.read_text(encoding='utf-8')
                break

        if not content:
            return None

        id_match = re.search(r'(\d+-[a-z0-9]+\.apps\.googleusercontent\.com)', content)
        secret_match = re.search(r'(GOCSPX-[A-Za-z0-9_-]+)', content)
        
        if id_match and secret_match:
            return {"clientId": id_match.group(1), "clientSecret": secret_match.group(1)}
    except Exception:
        return None

    return None

def main():
    print("--- Gemini CLI Credential Helper ---")
    creds = extract_gemini_cli_credentials()
    
    if creds:
        print("✅ Credentials extracted successfully from local gemini-cli!")
        print("\n" + "="*50)
        print("COPY THE FOLLOWING FOR YOUR REMOTE SETUP:")
        print("="*50)
        print(f"CLIENT_ID: {creds['clientId']}")
        print(f"CLIENT_SECRET: {creds['clientSecret']}")
        print("="*50 + "\n")
        print("You will need these when setting up Gemini CLI Auth on your remote server.")
    else:
        print("❌ Could not find gemini-cli or credentials automatically.")
        print("\nIf you are running this on a machine where gemini-cli is NOT installed,")
        print("please run this script on a machine that DOES have gemini-cli installed")
        print("and copy the output below.\n")
        
        client_id = input("Enter Gemini Client ID: ").strip()
        client_secret = input("Enter Gemini Client Secret: ").strip()
        
        if client_id and client_secret:
            creds = {"clientId": client_id, "clientSecret": client_secret}
            print("\n✅ Credentials recorded manually.")
        else:
            print("❌ No credentials provided. Auth flow will not be possible.")
            sys.exit(1)

    # For internal use by auth service
    return creds

if __name__ == "__main__":
    main()
