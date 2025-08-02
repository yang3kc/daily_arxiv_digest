import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class ActivityLogger:
    def __init__(self, log_file: str = "logs/activity.jsonl"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log_activity(
        self, action: str, status: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log an activity with timestamp and metadata.

        Args:
            action: Type of action ("fetch_papers", "llm_processing", "complete_run")
            status: Status of action ("started", "completed", "failed")
            metadata: Additional context data
        """
        now = datetime.now()
        log_entry = {
            "timestamp": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "action": action,
            "status": status,
            "metadata": metadata or {},
        }

        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def get_logs_by_date(self, date: str) -> List[Dict[str, Any]]:
        """Get all log entries for a specific date.

        Args:
            date: Date in YYYY-MM-DD format

        Returns:
            List of log entries for the specified date
        """
        if not self.log_file.exists():
            return []

        logs = []
        with open(self.log_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("date") == date:
                        logs.append(entry)
                except json.JSONDecodeError:
                    continue

        return logs

    def has_run_today(self) -> bool:
        """Check if the system has completed a full run today.

        Returns:
            True if a complete_run with status "completed" exists for today
        """
        today = datetime.now().strftime("%Y-%m-%d")
        today_logs = self.get_logs_by_date(today)

        return any(
            log.get("action") == "complete_run" and log.get("status") == "completed"
            for log in today_logs
        )

    def get_recent_logs(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get logs from the last N days.

        Args:
            days: Number of days to look back

        Returns:
            List of log entries from the last N days
        """
        if not self.log_file.exists():
            return []

        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d")

        logs = []
        with open(self.log_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("date") >= cutoff_str:
                        logs.append(entry)
                except json.JSONDecodeError:
                    continue

        return sorted(logs, key=lambda x: x.get("timestamp", ""))


# Global logger instance
logger = ActivityLogger()
