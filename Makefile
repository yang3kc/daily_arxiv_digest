.PHONY: run, help, all, check-log

all: run

help:
	@echo "Usage: make [target]"
	@echo "Targets:"
	@echo "  all - Run the streamlit app"
	@echo "  run - Run the streamlit app"
	@echo "  check-log - Check activity logs"
	@echo "  help - Display this help message"

run:
	uv run streamlit run arxiv_digest.py

check-log:
	uv run python check_log.py