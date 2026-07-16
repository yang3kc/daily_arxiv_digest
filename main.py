import argparse
import json
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from src.digest import run_digest

load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description="Generate a daily arXiv digest (digest.md + digest.json)."
    )
    parser.add_argument(
        "--config", default="config.json", help="Path to the config file"
    )
    parser.add_argument(
        "--date",
        default=date.today().isoformat(),
        help="Date label (YYYY-MM-DD) for the output folder; the arXiv feed "
        "always returns the latest announcement, so this only names the output",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate even if the digest for this date already exists",
    )
    args = parser.parse_args()

    if not Path(args.config).exists():
        print(
            f"Config file '{args.config}' not found; "
            "copy config.example.json to config.json and edit it."
        )
        return 1

    with open(args.config) as f:
        config = json.load(f)

    output_dir = Path(config.get("output_dir", "digests")) / args.date
    json_path = output_dir / "digest.json"
    if json_path.exists() and not args.force:
        print(f"Digest for {args.date} already exists at {json_path}; use --force to regenerate.")
        return 0

    digest, json_path, md_path = run_digest(config, args.date, output_dir)
    stats = digest["stats"]
    print(
        f"Selected {stats['papers_selected']} of {stats['papers_fetched']} papers."
    )
    print(f"Wrote {json_path}, {md_path}, and {json_path.parent / 'scores.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
