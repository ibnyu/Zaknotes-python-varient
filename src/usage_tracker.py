import json
import os
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class UsageTracker:
    def __init__(self, usage_file: str = "usage_stats.json"):
        self.usage_file = usage_file
        self.stats = self._load_stats()

    def _load_stats(self) -> Dict[str, Dict[str, int]]:
        if not os.path.exists(self.usage_file):
            return {}
        try:
            with open(self.usage_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def _save_stats(self):
        try:
            with open(self.usage_file, 'w') as f:
                json.dump(self.stats, f, indent=4)
        except IOError as e:
            logger.error(f"Error saving usage stats: {e}")

    def record_usage(self, email: str, model_name: str):
        """Records a single request for a given email and model."""
        if email not in self.stats:
            self.stats[email] = {}
        
        if model_name not in self.stats[email]:
            self.stats[email][model_name] = 0
            
        self.stats[email][model_name] += 1
        self._save_stats()

    def get_usage_report(self) -> Dict[str, Dict[str, int]]:
        """Returns the full usage statistics."""
        return self.stats
