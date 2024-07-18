import cohere, json
import dotenv
import os
dotenv.load_dotenv()
import logging
import requests
import time

import streamlit as st

st.set_page_config(page_title="Cohere AI Deal Analysis", page_icon='🧠')
st.title("Cohere AI Deal Analysis")
st.write("### Create Structured Data Using Cohere AI.")

st.write('''Enter a URL below of a deal memo, funding announcement, or press release about a recent venture capital investment.  The app will use [Cohere](https://cohere.com/) to analyze the text and return structured data in JSON format.  

''')

with st.sidebar:
    st.write('''## About this App
This app uses the Cohere AI API to analyze a adeal announcement from a URL.  It will return structured data in JSON format.''')

    st.write('''
         
## Demonstrating Structured Data Extraction
In this example, the model will take in unstructured data from the web, and return a structured JSON object with the data.  Specifically, it reads a press release about a recent venture capital investment and and extracts structured data from it, such as the name of the company, the funding round, the investment amount, cofounders, and valuation.  This is useful for tracking investments in the startup ecosystem, and for understanding the trends in venture capital funding.

## Why is this interesting?  
Data comes from across the web in unstructured format.  Organizing the data is the first step in developing better business intelligence.

## A Cohere AI Example
This example uses the [Cohere AI API](https://docs.cohere.com/) backend to perform an analysis on the memo and return a structured JSON response.           

## See the Code
You can see the code for this app on [GitHub](https://github.com/johnisanerd/cohere_analyze_press_release)
''')


# Example Deal: https://www.reuters.com/technology/ai-startup-cohere-seeks-5-bln-valuation-latest-fundraising-source-says-2024-03-21/
# Example Deal: "https://techcrunch.com/2023/06/08/ai-startup-cohere-now-valued-at-over-2-1b-raises-270m/"

url_to_scrape = "https://techcrunch.com/2023/06/08/ai-startup-cohere-now-valued-at-over-2-1b-raises-270m/"

# Setup ratelimiting for Jinja AI API
# https://requests-ratelimiter.readthedocs.io
from requests_ratelimiter import LimiterSession
requests_session = LimiterSession(per_minute=20)    # Create a rate limiter that allows 20 calls per minute

# This is an example deal we will ask the LLM to analyze the deal memo txt with.
schema_structure = { "type": "json_object",
                    "schema": {
                        "type": "object",
                        "required": ["company_name", "company_description", "funding_type", "startup_vertical"],
                        "properties": {
                            'company_name': { "type": "string" },
                            'company_url': { "type": "string" },
                            'startup_vertical': { "type": "string" },
                            'location_country': { "type": "string" },
                            'location_state': { "type": "string" },
                            'location_city': { "type": "string" },
                            'company_description': { "type": "string" },
                            'founding_year': { "type": "string" },
                            'funding_type': { "type": "string" },
                            'funding_amount_millions': { "type": "integer" },
                            'valuation_millions': { "type": "integer" },
                            'coinvestors': { "type": "string" },
                            'premoney_valualtion_millions': { "type": "integer" },
                            'revenue': { "type": "boolean" },
                            'prominent_investors_mentioned': { "type": "string" },
                            'founders': { "type": "string" }
                        }
    }
}

# Load the API key from the .env file
COHERE_API_KEY = os.environ["COHERE_API_KEY"]
co = cohere.Client(api_key=COHERE_API_KEY)

def scrape_jina_ai(url: str) -> str:
    '''
    Scrape the page using Jinja AI.  Return the text.
    If it fails, it will return a 404, a 422.
    If it successeds, response will be a 200.
    Get the status code with response.status_code.
    Get the resolved url with response.url.
    Get the text response with response.text.
    '''
    logging.info(f"Scraping url with Jina AI: {url} ")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Referer": "https://www.google.com/",
        "Upgrade-Insecure-Requests": "1"
    }

    # Get the redirect first.
    try:
        cleaned_response = requests.get(url, allow_redirects=True, headers=headers)
        url = cleaned_response.url
    except:
        pass

    requests_session.headers.update(headers)
    try:
        response = requests_session.get("https://r.jina.ai/" + url, allow_redirects=True, headers=headers, timeout=60)

    except:
        return False

    if response.status_code == 429: # Check if the rate limit has been reached
            seconds_to_wait = int(response.headers["Retry-After"]) # Get the number of seconds to wait from the Retry-After header
            logging.error(f"Rate limit exceeded for {url}. Waiting {seconds_to_wait} seconds before retrying...") # Print a message
            time.sleep(seconds_to_wait) # Wait for the specified time
            return scrape_jina_ai(url) # Recursively call the function again until the rate limit is lifted

    return response

def analyze_deal(url: str) -> str:
    # Get the deal text from the URL
    try:
        deal = scrape_jina_ai(url_to_scrape)
        if deal:
            deal_text = deal.text
            # st.write("### Deal Text")
            # st.write("The following text was scraped from the URL provided:  ")
            # st.write(deal_text[:1000])
        else:
            logging.error("Failed to scrape the deal text from the URL.")
            st.write("An error occurred while trying to scrape the deal text from the URL.")
            return False
    except:
        logging.error("Failed to scrape the deal text from the URL.")
        st.write("An error occurred while trying to scrape the deal text from the URL.")
        return False
    
    deal = co.chat(
        # Documentation at: https://docs.cohere.com/reference/chat
        model="command-r-plus",
        preamble="Analyze the following deal text from a press release.",
        message=f'''
        This is the deal in markdown format: {deal_text}
        Return formatted JSON.
        ''',
        response_format=schema_structure
    )

    logging.info(deal.text)

    return deal.text

str_request_text = 'Enter the url of the deal to analyze.'
str_question_text_default = url_to_scrape

str_submit_button_text = 'Strap in, let\'s go!'
str_submit_button_help_text = 'Click to submit for analysis.'

# https://docs.streamlit.io/library/api-reference/widgets/st.text_area
request = st.text_input(str_request_text, 
            value=str_question_text_default, 
            max_chars=1000, 
            key='request-text-area',  # unique key for text_area widget                    help=None, 
            on_change=None, 
            args=None, 
            kwargs=None, 
            placeholder=None, 
            disabled=False, 
            label_visibility="visible"
            )

btn = st.button(str_submit_button_text, 
            key='submit_button', 
            help=str_submit_button_help_text,  
            kwargs=None, 
            type="primary", 
            disabled=False, 
            use_container_width=False)

if btn:
    st.divider()
    logging.info(f"Analyzing the deal from the URL: {request}")
    with st.spinner('Processing results . . . '):
        analyzed_deal_string = analyze_deal(request)
        st.write(f"Finished analyzing the deal!")

    st.divider()
    analyzed_deal_json = json.loads(analyzed_deal_string)   # analyzed_deal_string is a string in JSON format.  Prettify it.

    # Display the JSON in a pretty format.
    st.write("### Structured Data")
    st.write(analyzed_deal_json)
