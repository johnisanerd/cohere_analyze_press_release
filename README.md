# Cohere Demo

This example app uses the Cohere AI API to analyze a Venture Capital investment announcement from a URL, and returns structured data in JSON format.  This is a powerful example of taking unstructured data (such as a press release or written memo) and extracting structured data from it.  This is a common use case in the business world, where data comes in many forms and needs to be organized for analysis.  Cohere offers a set of LLM's "Built on the language of business" that are optimized for this type of task.

## Demonstrating Structured Data Extraction

In this example, the model will take in unstructured data from the web, and return a structured JSON object with the data. Specifically, it reads a press release about a recent venture capital investment and and extracts structured data from it, such as the name of the company, the funding round, the investment amount, cofounders, and valuation. This is useful for tracking investments in the startup ecosystem, and for understanding the trends in venture capital funding.

## Try It

Try the demo app, [using an example deal](https://techcrunch.com/2023/06/08/ai-startup-cohere-now-valued-at-over-2-1b-raises-270m/), [here on Streamlit](https://cohereanalyzepressrelease.streamlit.app/).


# Developers

## API Key Setup

You will need your own Cohere API key to run this example.  Setup an account and go to the [Cohere dashboard to set them up here](https://dashboard.cohere.com/api-keys).  Create a ".env" file in the root directory and add the following:

```bash
COHERE_API_KEY="Your API Key Here"
```

## Virtual Environment Setup

```bash
python3.11 -m venv .venv202407
source .venv202407/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

## Running the App

```bash
streamlit run app.py
```