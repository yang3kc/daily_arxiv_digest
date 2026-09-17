import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

from dotenv import load_dotenv

from src.digest import output_paths, rethreshold_digest, run_digest

load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description="Generate a daily arXiv digest (digest-<date>.json)."
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
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="Also write digest-<date>.md, the human-readable rendering; "
        "off by default, the JSON files are always written",
    )
    parser.add_argument(
        "--rethreshold",
        type=float,
        metavar="X",
        help="Rebuild digest-<date>.json from the saved "
        "scores-<date>.json at threshold X — no fetching or re-scoring; TL;DRs "
        "are only generated for papers newly above the threshold",
    )
    args = parser.parse_args()

    if not DATE_RE.match(args.date):
        print(
            f"Invalid --date '{args.date}'; expected YYYY-MM-DD "
            "(it names the output folder and is stamped into the filenames)."
        )
        return 1

    if not Path(args.config).exists():
        print(
            f"Config file '{args.config}' not found; "
            "copy config.example.json to config.json and edit it."
        )
        return 1

    with open(args.config) as f:
        config = json.load(f)

    output_dir = Path(config.get("output_dir", "digests")) / args.date

    if args.rethreshold is not None:
        digest, json_path, md_path = rethreshold_digest(
            config, args.date, output_dir, args.rethreshold, markdown=args.markdown
        )
        stats = digest["stats"]
        print(
            f"Re-thresholded at {args.rethreshold}: "
            f"{stats['papers_selected']} of {stats['papers_fetched']} papers."
        )
        written = [str(json_path)] + ([str(md_path)] if md_path else [])
        print(f"Rewrote {' and '.join(written)}")
        return 0

    paths = output_paths(output_dir, args.date)
    json_path = paths["json"]
    if json_path.exists() and not args.force:
        print(f"Digest for {args.date} already exists at {json_path}; use --force to regenerate.")
        return 0

    digest, json_path, md_path = run_digest(
        config, args.date, output_dir, markdown=args.markdown
    )
    stats = digest["stats"]
    print(
        f"Selected {stats['papers_selected']} of {stats['papers_fetched']} papers."
    )
    written = [str(json_path)] + ([str(md_path)] if md_path else []) + [str(paths["scores"])]
    print(f"Wrote {', '.join(written[:-1])}, and {written[-1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
