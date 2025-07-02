# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Daily arXiv Digest is a tool that uses OpenAI's ChatGPT to automatically filter and select interesting arXiv papers based on user-defined topics. It fetches papers from arXiv RSS feeds, evaluates them using LLM, and presents results through a Streamlit web interface.

## Commands

### Development and Running
- `make run` or `make all` - Launch the Streamlit application
- `uv run streamlit run arxiv_digest.py` - Direct command to run the app
- `uv sync` - Install/update dependencies

### Testing
- `python test_llm.py` - Run the basic integration test for RSS fetching and LLM processing

## Architecture

### Core Components
- `arxiv_digest.py` - Main Streamlit application entry point
- `src/rss.py` - ArxivRSS class handles fetching papers from arXiv RSS feeds
- `src/llm.py` - LLMPaperReader class manages OpenAI API calls for paper evaluation
- `src/utils.py` - Utility functions

### Key Design Patterns
- **Concurrent Processing**: Uses ThreadPoolExecutor with 50 concurrent tasks by default for parallel paper evaluation
- **Error Resilience**: Implements retry logic with graceful fallbacks for API failures
- **Structured Output**: Uses Pydantic models for type-safe JSON parsing of LLM responses
- **Configuration-Driven**: All settings (topics, arXiv subjects, model parameters) are in `config.json`

### Data Flow
1. Fetch papers from configured arXiv RSS feeds (`arxiv_subjects` in config.json)
2. Concurrently evaluate papers using OpenAI API with structured prompts
3. Display filtered results in Streamlit interface with relevance scores

## Configuration

### Environment Requirements
- Requires `OPENAI_API_KEY` environment variable
- Python 3.12+ required
- Uses `uv` package manager

### Key Configuration Files
- `config.json` - Contains arXiv subjects to monitor, research topics of interest, OpenAI model settings, and concurrency parameters
- `pyproject.toml` - Project dependencies and metadata

### Current Configuration Focus
- Monitors CS.CY (Computers and Society) and CS.CL (Computation and Language) arXiv categories
- 7 specific AI/ML research topics focused on AI security, applications, and factuality
- Uses GPT-4.1-mini model with 40-second timeout

## Development Notes

### Threading Architecture
- Project evolved from async to threading-based concurrency (see experiments in `exps/` directory)
- Current implementation uses ThreadPoolExecutor for better reliability with OpenAI API

### Error Handling Strategy
- LLM evaluation failures return neutral scores to prevent batch failures
- Implements retry logic for API timeouts and errors
- Progress tracking in Streamlit interface shows real-time status

### Experimental Development
- `exps/` directory contains Jupyter notebooks with development iterations and concurrency experiments
- Key notebooks: `structured_threading.ipynb`, `async.ipynb` show evolution of concurrent processing approach