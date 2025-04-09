.PHONY: run, help

help:
	@echo "Usage: make [target]"
	@echo "Targets:"
	@echo "  run - Run the streamlit app"
	@echo "  help - Display this help message"

run:
	uv run streamlit run arxiv_digest.py