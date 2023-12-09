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

The tool was developed under Python 3.10.
You can install the dependencies with:

```sh
pip install -r requirements.txt
```

## Usage

Modify the configuration file at `config.json`.
Specifically, change the arXiv subject you want to follow and the topics you are interested.
You can also change the OpenAI model, but make sure the model support JSON mode.

You can run the tool by:

```sh
python main.py
```

This would fetch the information about the newest arXiv papers through RSS feeds then use ChatGPT to evaluate the papers.

Then you can run

```sh
streamlit run streamlit_app.py
```

To start a web interface to inspect the results.

# Disclaimer

This tool is mainly built for my personal use.
The stability of it will not be guaranteed.
Use at your own discretion.