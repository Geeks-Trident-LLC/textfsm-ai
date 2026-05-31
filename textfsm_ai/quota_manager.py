import json
import time
from pathlib import Path


class QuotaManager:
    def __init__(self, provider_name: str, daily_limit: int, monthly_limit: int):
        self.provider = provider_name
        self.daily_limit = daily_limit
        self.monthly_limit = monthly_limit

        self.path = Path.home() / f".textfsm_ai_usage_{provider_name}.json"
        self._load()

    def _load(self):
        if self.path.exists():
            with open(self.path, "r") as f:
                self.data = json.load(f)
        else:
            self.data = {
                "day": self._today(),
                "month": self._month(),
                "daily_tokens": 0,
                "monthly_tokens": 0,
                "just_reset_month": False,
            }
            self._save()

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f)

    def _today(self):
        return time.strftime("%Y-%m-%d")

    def _month(self):
        return time.strftime("%Y-%m")

    def _maybe_reset(self):
        today = self._today()
        month = self._month()

        # Monthly reset
        if self.data["month"] != month:
            self.data["month"] = month
            self.data["monthly_tokens"] = 0
            self.data["day"] = today
            self.data["daily_tokens"] = 0
            self.data["just_reset_month"] = True
            self._save()
            return

        # Daily reset
        if self.data["day"] != today:
            self.data["day"] = today
            self.data["daily_tokens"] = 0
            self.data["just_reset_month"] = False
            self._save()
            return

    def allowed(self, count: int) -> bool:
        self._maybe_reset()

        # Monthly limit always enforced
        if self.data["monthly_tokens"] + count > self.monthly_limit:
            return False

        # Daily limit skipped ONCE after monthly reset
        if not self.data.get("just_reset_month", False):
            if self.data["daily_tokens"] + count > self.daily_limit:
                return False

        return True

    def add_tokens(self, count: int):
        self._maybe_reset()

        # After first request of new month, daily limit applies again
        if self.data.get("just_reset_month", False):
            self.data["just_reset_month"] = False

        self.data["daily_tokens"] += count
        self.data["monthly_tokens"] += count
        self._save()
