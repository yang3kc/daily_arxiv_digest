# Introduction

Using ChatGPT to select interesting arXiv papers everyday.

Having trouble catching up with the new arXiv papers everyday?
This tool uses ChatGPT to read the latest arXiv papers and select the ones relevant to the topics of your interest!

# How to use

## OpenAI key

The model relies on OpenAI's models.
So please provide your OpenAI key and export them to an environment variable named `OPENAI_API_KEY`:

```sh
export OPENAI_API_KEY=YOUR_OPENAI_KEY
```

## Dependency

The tool was developed under Python 3.12.
It uses [uv](https://docs.astral.sh/uv/) to manage the dependencies.
You can install the dependencies with:

```sh
uv sync
```

## Usage

Modify the configuration file at `config.json`.
Specifically, change the arXiv subject you want to follow and the topics you are interested.
You can also change the OpenAI model, but make sure the model support JSON mode.

You can run the tool by:

```sh
uv run streamlit run arxiv_digest.py
```

A web interface will be launched, where you can fetch the fresh papers and have ChatGPT evaluate them for you.
You can then inspect the results in the web interface.

# Disclaimer

This tool is mainly built for my personal use.
The stability of it will not be guaranteed.
Use at your own discretion.