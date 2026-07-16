.PHONY: run, help, all, check-log

all: run

help:
	@echo "Usage: make [target]"
	@echo "Targets:"
	@echo "  all - Generate today's digest"
	@echo "  run - Generate today's digest"
	@echo "  check-log - Check activity logs"
	@echo "  help - Display this help message"

run:
	uv run python main.py

check-log:
	uv run python check_log.py
