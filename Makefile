.PHONY: run, help, all, check-log, test

all: run

help:
	@echo "Usage: make [target]"
	@echo "Targets:"
	@echo "  all - Generate today's digest"
	@echo "  run - Generate today's digest"
	@echo "  test - Run offline rendering unit tests"
	@echo "  check-log - Check activity logs"
	@echo "  help - Display this help message"

run:
	uv run python main.py

test:
	uv run python test_digest.py

check-log:
	uv run python check_log.py
