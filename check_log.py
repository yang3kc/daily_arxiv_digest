#!/usr/bin/env python3
"""
Check daily arXiv digest activity logs.

This script shows whether the system has run today and displays recent activity.
"""

from collections import defaultdict
from datetime import datetime

from src.logger import logger


def format_status(status: str) -> str:
    """Format status with color codes."""
    colors = {
        "started": "\033[93m⏳\033[0m",  # Yellow
        "completed": "\033[92m✅\033[0m",  # Green
        "failed": "\033[91m❌\033[0m",  # Red
    }
    return colors.get(status, status)


def format_action(action: str) -> str:
    """Format action names for display."""
    action_names = {
        "fetch_papers": "Fetch Papers",
        "llm_processing": "LLM Processing",
        "complete_run": "Complete Run",
    }
    return action_names.get(action, action)


def show_today_status():
    """Show today's activity status."""
    today = datetime.now().strftime("%Y-%m-%d")
    today_logs = logger.get_logs_by_date(today)

    print(f"\n📅 Today's Status ({today})")
    print("=" * 40)

    if not today_logs:
        print("🟡 No activity recorded today")
        return

    # Group logs by action
    actions = defaultdict(list)
    for log in today_logs:
        actions[log.get("action", "unknown")].append(log)

    # Show status for each action type
    for action, logs in actions.items():
        latest_log = max(logs, key=lambda x: x.get("timestamp", ""))
        status = latest_log.get("status", "unknown")
        metadata = latest_log.get("metadata", {})

        print(f"{format_status(status)} {format_action(action)}")

        # Show relevant metadata
        if action == "fetch_papers" and "paper_count" in metadata:
            print(f"   📄 Papers fetched: {metadata['paper_count']}")
        elif action == "llm_processing" and "papers_processed" in metadata:
            processed = metadata.get("papers_processed", 0)
            total = metadata.get("papers_total", 0)
            print(f"   🤖 Papers processed: {processed}/{total}")

    # Overall status
    has_completed_run = logger.has_run_today()
    if has_completed_run:
        print("\n🎉 System has completed a full run today!")
    else:
        print("\n⚠️  System has not completed a full run today")


def show_recent_activity():
    """Show activity from the last 7 days."""
    print("\n📊 Recent Activity (Last 7 days)")
    print("=" * 40)

    recent_logs = logger.get_recent_logs(7)

    if not recent_logs:
        print("No recent activity recorded")
        return

    # Group by date
    by_date = defaultdict(list)
    for log in recent_logs:
        by_date[log.get("date", "unknown")].append(log)

    # Show summary for each date
    for date in sorted(by_date.keys(), reverse=True):
        logs = by_date[date]

        # Check if there was a complete run
        complete_runs = [
            l
            for l in logs
            if l.get("action") == "complete_run" and l.get("status") == "completed"
        ]

        if complete_runs:
            # Get paper counts from the run
            fetch_logs = [
                l
                for l in logs
                if l.get("action") == "fetch_papers" and l.get("status") == "completed"
            ]
            llm_logs = [
                l
                for l in logs
                if l.get("action") == "llm_processing"
                and l.get("status") == "completed"
            ]

            paper_count = 0
            processed_count = 0

            if fetch_logs:
                paper_count = fetch_logs[-1].get("metadata", {}).get("paper_count", 0)
            if llm_logs:
                processed_count = (
                    llm_logs[-1].get("metadata", {}).get("papers_processed", 0)
                )

            print(
                f"✅ {date}: Complete run ({paper_count} papers, {processed_count} processed)"
            )
        else:
            # Show partial activity
            activity_types = set(log.get("action") for log in logs)
            print(f"⚠️  {date}: Partial activity ({', '.join(activity_types)})")


def show_statistics():
    """Show usage statistics."""
    print("\n📈 Statistics")
    print("=" * 40)

    recent_logs = logger.get_recent_logs(30)  # Last 30 days

    if not recent_logs:
        print("No data available for statistics")
        return

    # Count complete runs
    complete_runs = [
        l
        for l in recent_logs
        if l.get("action") == "complete_run" and l.get("status") == "completed"
    ]

    # Count by date
    run_dates = set(log.get("date") for log in complete_runs)

    print(f"📅 Days with complete runs (last 30 days): {len(run_dates)}")
    print(f"🔄 Total complete runs: {len(complete_runs)}")

    # Average papers processed
    llm_logs = [
        l
        for l in recent_logs
        if l.get("action") == "llm_processing" and l.get("status") == "completed"
    ]
    if llm_logs:
        paper_counts = [
            l.get("metadata", {}).get("papers_processed", 0) for l in llm_logs
        ]
        avg_papers = sum(paper_counts) / len(paper_counts) if paper_counts else 0
        print(f"📄 Average papers processed per run: {avg_papers:.1f}")


def main():
    """Main function."""
    print("🔍 Daily arXiv Digest - Activity Log Checker")

    show_today_status()
    show_recent_activity()
    show_statistics()

    print("\n" + "=" * 40)
    print("Use 'make run' to start the system")


if __name__ == "__main__":
    main()
