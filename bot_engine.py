from browser_driver import BrowserDriver
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import time
import os

# --- CONFIGURATION ---
TARGET_MODEL_NAME = "Gemini 2.5 Pro"
TARGET_MODEL_ID = "model-carousel-row-models/gemini-2.5-pro"
TARGET_SYSTEM_PROMPT = "transcriptor" 

class AIStudioBot:
    def __init__(self):
        self.driver = BrowserDriver()
        self.page = None

    def start_session(self):
        print("🤖 Bot: Connecting to session...")
        if not self.driver.connect(): 
            raise Exception("Could not connect to browser.")
        
        context = self.driver.context
        # Grant clipboard permissions
        context.grant_permissions(["clipboard-read", "clipboard-write"])
        
        found = False
        for p in context.pages:
            if "aistudio" in p.url:
                self.page = p
                found = True
                p.bring_to_front()
                break
        
        if not found:
            print("   Opening new AI Studio tab...")
            self.page = context.new_page()
            self.page.goto("https://aistudio.google.com/prompts/new_chat")
        
        try: self.page.wait_for_load_state("networkidle", timeout=10000)
        except: pass

    def select_model(self):
        print(f"🤖 Bot: Checking Model ({TARGET_MODEL_NAME})...")
        try:
            card = self.page.locator(".model-selector-card").first
            try: card.wait_for(state="visible", timeout=8000)
            except: pass
            
            if not card.is_visible():
                print("   ⚠️ Model card not visible. Proceeding blindly...")
            else:
                current_text = card.text_content().strip()
                if TARGET_MODEL_NAME in current_text:
                    print(f"   ✅ Already on {TARGET_MODEL_NAME}.")
                    return
                
                print("   Switching Model...")
                card.click()
                
                # Try clicking All
                try:
                    all_btn = self.page.locator("button[data-test-category-button='']").filter(has_text="All")
                    all_btn.wait_for(state="visible", timeout=3000)
                    all_btn.click()
                except: pass

                # Click ID
                model_btn = self.page.locator(f'button[id="{TARGET_MODEL_ID}"]')
                if model_btn.count() > 0:
                    model_btn.scroll_into_view_if_needed()
                    model_btn.click(timeout=5000)
                    print(f"   ✅ Switched to {TARGET_MODEL_NAME}")
                else:
                    print(f"   ⚠️ {TARGET_MODEL_NAME} ID not found.")
                
                try: self.page.get_by_label("Close panel").click(timeout=2000)
                except: pass
        except Exception as e:
            print(f"   ❌ Model selection error: {e}")

    def set_system_prompt(self, prompt_name):
        print(f"🤖 Bot: Setting System Prompt ({prompt_name})...")
        try:
            self.page.locator("button[data-test-system-instructions-card]").click()
            self.page.wait_for_timeout(1000)
            self.page.locator(".mat-mdc-select-trigger").last.click()
            self.page.wait_for_timeout(1000)
            
            option = self.page.locator("mat-option").filter(has_text=prompt_name).first
            try:
                option.wait_for(state="visible", timeout=3000)
                option.click()
                print(f"   ✅ Selected: {prompt_name}")
            except:
                print(f"   ❌ Prompt '{prompt_name}' not found.")
            
            time.sleep(1)
            try: self.page.get_by_label("Close panel").click()
            except: pass
        except Exception as e:
            print(f"   ❌ System Prompt failed: {e}")

    def upload_and_transcribe(self, audio_path, output_path="transcript.txt"):
        if not os.path.exists(audio_path):
            print(f"❌ File not found: {audio_path}")
            return None

        print(f"🤖 Bot: Uploading {os.path.basename(audio_path)}...")
        
        try:
            # 1. CLICK PLUS
            self.page.locator("button[data-test-add-chunk-menu-button]").click()
            self.page.wait_for_timeout(2000) 

            # 2. CLICK UPLOAD FILE
            try:
                with self.page.expect_file_chooser(timeout=10000) as fc_info:
                    self.page.get_by_text("Upload File", exact=False).click()
                fc_info.value.set_files(audio_path)
                print("   ✅ File uploaded.")
            except Exception as e:
                print(f"   ❌ Upload Dialog Failed: {e}")
                return None

            # 3. WAIT FOR RUN
            print("   Waiting for 'Run'...")
            run_btn = self.page.locator(".run-button").first
            
            for i in range(90):
                if run_btn.is_enabled():
                    run_btn.click()
                    print("   🚀 Run Clicked!")
                    break
                time.sleep(1)
            else:
                print("   ❌ Timeout: Run button never enabled.")
                run_btn.click(force=True)

            # 4. WAIT FOR GENERATION
            print("⏳ Waiting for generation...")
            for _ in range(20):
                if self.page.get_by_label("Stop generation").count() > 0: break
                time.sleep(1)
            
            while self.page.get_by_label("Stop generation").count() > 0:
                time.sleep(2)
            
            print("   Stop button gone. Verifying text stability...")
            
            # 5. FIND THE CORRECT RESPONSE
            # Logic: Find 'ms-chat-turn' that contains the 'Model' role div
            # This is the wrapper for the entire AI answer
            last_model_turn = self.page.locator("ms-chat-turn").filter(
                has=self.page.locator("[data-turn-role='Model']")
            ).last
            
            # Wait for it to exist
            last_model_turn.wait_for(state="visible", timeout=30000)
            
            # 6. STABILITY CHECK
            prev_len = 0
            stable_count = 0
            
            for _ in range(30): # 60 seconds max
                # We read text from the inner role div to be precise
                curr_text = last_model_turn.inner_text()
                curr_len = len(curr_text)
                
                if curr_len == prev_len and curr_len > 10:
                    stable_count += 1
                else:
                    stable_count = 0
                
                if stable_count >= 2:
                    print("   ✅ Text stabilized.")
                    break
                
                prev_len = curr_len
                time.sleep(2)

            # 7. COPY VIA MENU
            print("   Extracting text via Copy Menu...")
            try:
                # Hover over the wrapper to reveal buttons
                last_model_turn.hover()
                time.sleep(0.5)
                
                # Find the 'Open options' button INSIDE this wrapper
                more_btn = last_model_turn.locator("button[aria-label='Open options']")
                more_btn.click()
                
                # Click "Copy as markdown"
                # Use exact=True to avoid partial matches if possible, or keep it loose
                self.page.get_by_text("Copy as markdown").click()
                
                time.sleep(1)
                text = self.page.evaluate("navigator.clipboard.readText()")
                
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(text)
                
                print(f"   ✅ Transcript saved to: {output_path}")
                return text

            except Exception as e:
                print(f"   ⚠️ Copy Menu Failed ({e}). Using raw inner_text fallback.")
                text = last_model_turn.inner_text()
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(text)
                return text

        except Exception as e:
            print(f"❌ Transcription failed: {e}")
            return None

    def close(self):
        self.driver.close()

if __name__ == "__main__":
    bot = AIStudioBot()
    try:
        bot.start_session()
        bot.select_model()
        bot.set_system_prompt(TARGET_SYSTEM_PROMPT)
        
        test_file = "/mnt/ext/Downloads/Music/test.mp3" 
        if not os.path.exists(test_file):
            with open(test_file, "w") as f: f.write("dummy content")
        
        result = bot.upload_and_transcribe(test_file, "transcript.txt")
        if result:
            print(f"\n--- SUCCESS (Length: {len(result)}) ---")
            
    except Exception as e:
        print(f"CRASH: {e}")