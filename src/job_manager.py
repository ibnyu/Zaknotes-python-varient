import re
import json
import os
from datetime import datetime

HISTORY_FILE = "history.json"

class JobManager:
    def __init__(self):
        self.history = []
        self.load_history()

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r') as f:
                    self.history = json.load(f)
            except:
                self.history = []
        else:
            self.history = []

    def save_history(self):
        # Save entire history to file
        with open(HISTORY_FILE, 'w') as f:
            json.dump(self.history, f, indent=4)

    def get_pending_from_last_150(self):
        """
        Return list of jobs with status 'queue', 'failed', 'downloading', or 'processing' (for retry).
        Also includes granular intermediate states.
        Exclude 'no_link_found' from retry.
        """
        target_statuses = [
            'queue', 'failed', 'downloading', 'processing',
            'DOWNLOADED', 'SILENCE_REMOVED', 'BITRATE_MODIFIED', 'CHUNKED'
        ]
        # Use regex for TRANSCRIBING_CHUNK_N
        pending = []
        for job in self.history:
            status = job.get('status', '')
            if status in target_statuses or status.startswith('TRANSCRIBING_CHUNK_'):
                pending.append(job)
        return pending

    def cancel_pending(self):
        """Cancel ALL pending, failed, and stuck jobs in history"""
        target_statuses = [
            'queue', 'failed', 'downloading', 'processing',
            'DOWNLOADED', 'SILENCE_REMOVED', 'BITRATE_MODIFIED', 'CHUNKED'
        ]
        for job in self.history:
            status = job.get('status', '')
            if status in target_statuses or status.startswith('TRANSCRIBING_CHUNK_'):
                job['status'] = 'cancelled'
        self.save_history()

    def fail_pending(self):
        """Mark ALL pending, downloading, or processing jobs as failed"""
        target_statuses = [
            'queue', 'downloading', 'processing',
            'DOWNLOADED', 'SILENCE_REMOVED', 'BITRATE_MODIFIED', 'CHUNKED'
        ]
        for job in self.history:
            status = job.get('status', '')
            if status in target_statuses or status.startswith('TRANSCRIBING_CHUNK_'):
                # Preserve the current state in a separate field if it's granular
                if status not in ['queue', 'downloading', 'processing']:
                    job['last_granular_state'] = status
                job['status'] = 'failed'
        self.save_history()

    def update_job_status(self, job_id, status):
        """Update the status of a specific job by ID."""
        for job in self.history:
            if job.get('id') == job_id:
                old_status = job.get('status')
                if status == 'failed' and old_status not in ['queue', 'downloading', 'processing', 'failed', 'completed', 'cancelled']:
                    job['last_granular_state'] = old_status
                job['status'] = status
                self.save_history()
                return True
        return False

    def get_job(self, job_id):
        """Get a specific job by ID."""
        for job in self.history:
            if job.get('id') == job_id:
                return job
        return None

    def smart_split(self, text):
        """Splits by comma/pipe/newline but respects (groups)"""
        if not text: return []
        pattern = r'[|;,\n](?![^(]*\))'
        parts = re.split(pattern, text)
        return [p.strip() for p in parts if p.strip()]

    def parse_group(self, text):
        """Removes parens () and splits content by comma"""
        text = text.strip()
        if text.startswith("(") and text.endswith(")"):
            content = text[1:-1]
            return [x.strip() for x in content.split(",") if x.strip()]
        return [text]

    def add_jobs(self, name_input, url_input):
        name_slots = self.smart_split(name_input)
        url_slots = self.smart_split(url_input)
        
        new_jobs = []
        
        # LOGIC CHECK: 1 Name, Many URL Slots?
        if len(name_slots) == 1 and len(url_slots) > 1:
            base_name = name_slots[0]
            global_counter = 1
            
            for i, u_slot in enumerate(url_slots):
                # Check for groups inside this slot too
                urls_in_slot = self.parse_group(u_slot)
                
                for url in urls_in_slot:
                    job_name = f"{base_name} {global_counter}"
                    new_jobs.append({
                        "id": f"{datetime.now().timestamp()}_{i}_{global_counter}",
                        "name": job_name,
                        "url": url,
                        "status": "queue",
                        "added_at": str(datetime.now())
                    })
                    global_counter += 1

        else:
            # Standard Logic (Slot to Slot mapping)
            for i, url_slot in enumerate(url_slots):
                # Get Name
                if i < len(name_slots):
                    base_name = name_slots[i]
                else:
                    base_name = f"Untitled {i+1}"

                # Expand URL Group
                expanded_urls = self.parse_group(url_slot)
                
                if len(expanded_urls) > 1:
                    # Multiple URLs in one slot -> Number them
                    for j, url in enumerate(expanded_urls):
                        job_name = f"{base_name} {j+1}"
                        new_jobs.append({
                            "id": f"{datetime.now().timestamp()}_{i}_{j}",
                            "name": job_name,
                            "url": url,
                            "status": "queue",
                            "added_at": str(datetime.now())
                        })
                else:
                    # Single URL in slot -> Keep name as is
                    new_jobs.append({
                        "id": f"{datetime.now().timestamp()}_{i}",
                        "name": base_name,
                        "url": expanded_urls[0],
                        "status": "queue",
                        "added_at": str(datetime.now())
                    })
        
        self.history.extend(new_jobs)
        self.save_history()
        return new_jobs