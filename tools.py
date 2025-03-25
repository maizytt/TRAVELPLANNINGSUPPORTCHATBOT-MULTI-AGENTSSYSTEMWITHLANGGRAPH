
# Import librarieslibraries
from dotenv import load_dotenv
import os
import json
import requests
from bs4 import BeautifulSoup
import re
import tiktoken
import cohere
from langchain_community.tools.tavily_search import TavilySearchResults
from datetime import datetime, timedelta

# ===================== Load Environment ===================

with open(".env", "r") as f:
    for line in f:
        key, value = line.split("=")
        os.environ[key] = value.strip()


load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
os.environ["SERPER_API_KEY"] = os.getenv('SERPER_API_KEY')
os.environ["TAVILY_API_KEY"] = os.getenv('TAVILY_API_KEY')
os.environ['WEATHERMAP_API_KEY'] = os.getenv('WEATHERMAP_API_KEY')
os.environ["COHERE_API_KEY"] = os.getenv('COHERE_API_KEY')



# ======================== Tool ============================

# Tavily Tool 

tavily_tool = TavilySearchResults(max_results=5)


# Scraping contentcontent

def process_content(url: str) -> str:
    """Processes and extracts main content from a webpage.

    Args:
        url (str): The URL of the webpage to process.

    Returns:
        str: The extracted main content as text, or None if processing fails.
    """
    try:
        response = requests.get(url, verify=False, timeout=5) 
        response.raise_for_status() 

        soup = BeautifulSoup(response.content, 'html.parser')

        # Attempt to extract content from common main content tags
        main_content = soup.find('main') or soup.find('article')

        if not main_content:
            # Fallback: extract based on common class or id names
            main_content = soup.find(attrs={'class': 'content'}) or soup.find(attrs={'id': 'content'})

        # If still no content is found, fall back to entire page text
        return main_content.get_text(strip=True) if main_content else soup.get_text(strip=True)

    except (requests.RequestException, AttributeError) as e:

        print(f"Error processing {url}: {e}")
        return None



# Hàm giới hạn dictionary bằng cách chuyển thành chuỗi
def limit_tokens_from_dict(dictionary, max_tokens=128000):
    dict_str = str(dictionary)
    encoder = tiktoken.get_encoding("cl100k_base")
    tokens = encoder.encode(dict_str)

    if len(tokens) <= max_tokens:
        return dict_str

    limited_tokens = tokens[:max_tokens]
    limited_str = encoder.decode(limited_tokens)

    return limited_str

def split_content(content, max_tokens):
    """
    Chia nhỏ nội dung thành các phần nhỏ hơn dựa trên số lượng token tối đa.
    """
    encoder = tiktoken.get_encoding("cl100k_base")
    tokens = encoder.encode(content)
    chunks = [tokens[i:i+max_tokens] for i in range(0, len(tokens), max_tokens)]
    return [encoder.decode(chunk) for chunk in chunks]



# Serper Tool Google Search

def search_with_serper(query):
    """Search the internet about a given topic and return the relevant results"""
    top_result_to_return = 1
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': os.environ['SERPER_API_KEY'],
        'content-type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    if 'organic' not in response.json():
        return "Sorry, I couldn't find anything about that, there could be an error with your Serper API key."
    else:
        results = response.json()['organic']

        if len(results) > 0:
            return results[0]['link']
        else:
            return "No results found for your query."

def scrape_and_summarize_website(url: str) -> str:
        """
        Scrape and summarize content from a website using Cohere API.

        Args:
            url (str): The URL of the website to scrape.

        Returns:
            str: A summarized version of the content.
        """

        # Step 1: Fetch website content using ScrapeWebsiteTool
        response = process_content(url)

        # Step 2: Parse the HTML content into structured text
        content = response 

        # Step 3: Split content into manageable chunks
        max_chunk_size = 8000
        content_chunks = [content[i:i + max_chunk_size] for i in range(0, len(content), max_chunk_size)]

        # Step 4: Summarize each chunk using Cohere API
        co = cohere.Client(os.environ["COHERE_API_KEY"])  # Replace with your actual API key
        summaries = []
        for chunk in content_chunks:
            response = co.generate(
                model='command-xlarge-nightly',
                prompt=f"Please summarize the entire text without mentioning this article or this paragraph:\n\n{chunk}",
                max_tokens=300,
                temperature=0.5,
                stop_sequences=["--"]
            )
            summaries.append(response.generations[0].text.strip())

        # Combine all summaries
        return "\n\n".join(summaries)

def search_snippet(query):
    top_result_to_return = 1
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': os.environ['SERPER_API_KEY'],
        'content-type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    # check if there is an organic key
    if 'organic' not in response.json():
      return "Sorry, I couldn't find anything about that, there could be an error with you serper api key."
    else:
      results = response.json()['organic']

      return results[0]['snippet']

# # Serper Tool Google Search --> Return list urls
def list_search_with_serper(query, k = 5):
    """Search the internet about a given topic and return the relevant results"""
    top_result_to_return = k
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': os.environ['SERPER_API_KEY'],
        'content-type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    # Kiểm tra xem trong response có key 'organic' hay không
    if 'organic' not in response.json():
        return "Sorry, I couldn't find anything about that, there could be an error with your Serper API key."
    else:
        results = response.json()['organic']
        results = results[: top_result_to_return]

        # Kiểm tra nếu results là danh sách, và lấy link của kết quả đầu tiên
        if len(results) > 0:
            links = [result['link'] for result in results] #extract the 'link' from each element in the results list
            return links
        else:
          return "No results found for your query"

def list_scrape_and_summarize_website(url_list):
    """
    Scrape and summarize content from a list of websites using Cohere API.

    Args:
        url_list (list): A list of URLs to scrape and summarize.

    Returns:
        list: A list of summarized content from each webpage.
    """

    co = cohere.Client(os.environ['COHERE_API_KEY'])  
    summaries = []

    for url in url_list:
        # Step 1: Fetch website content using ScrapeWebsiteTool (a placeholder for the actual scraping tool)
        response = process_content(url)

        # Step 2: Assume the response is raw HTML content. For simplicity, we'll use the raw response as content
        content = response

        # Step 3: Split content into manageable chunks (max 8000 characters per chunk for Cohere API)
        max_chunk_size = 8000
        content_chunks = [content[i:i + max_chunk_size] for i in range(0, len(content), max_chunk_size)]

        # Step 4: Summarize each chunk using Cohere API
        for chunk in content_chunks:
            response = co.generate(
                model='command-xlarge-nightly',
                prompt=f"Please summarize the entire text without mentioning this article or this paragraph:\n\n{chunk}",
                max_tokens=300,
                temperature=0.5,
                stop_sequences=["--"]
            )
            summaries.append(response.generations[0].text.strip())

    return summaries


def convert_to_datetime(date_str: str):
    """
    Chuyển đổi chuỗi ngày tháng thành datetime và đặt thời gian thành 7:00 AM.
    """
    # Các định dạng ngày tháng có thể gặp
    date_formats = [
        "%d/%m/%y", "%m/%d/%y", "%d/%m/%Y", "%m/%d/%Y",
        "%d-%m-%y", "%d-%m-%Y", "%m-%d-%y", "%m-%d-%Y",
        "%d/%m/%y", "%d-%m-%y", "%d/%m/%Y", "%m/%d/%y",
        "%d/%m/%y", "%m/%d/%y", "%d-%m-%Y", "%y/%m/%d",
        "%Y/%m/%d", "%y-%m-%d", "%Y-%m-%d", "%Y/%m/%d"
    ]

    # Xử lý chuỗi đầu vào
    date_str = date_str.strip()  # Loại bỏ khoảng trắng thừa

    for fmt in date_formats:
        try:
            # Chuyển đổi chuỗi sang đối tượng datetime
            parsed_date = datetime.strptime(date_str, fmt)
            # Cập nhật thời gian thành 7:00 AM
            updated_date = parsed_date.replace(hour=7, minute=0, second=0, microsecond=0)
            return updated_date
        except ValueError:
            continue
    return date_str

def process_travel_duration(travel_duration):
    if type(travel_duration) == int:
      return travel_duration
    else:
      input_str = travel_duration.lower()
      days = 0

      match = re.match(r"(\d+)\s*ngày\s*(\d+)?\s*đêm?", input_str)
      if match:
          days = int(match.group(1))
          return days

      match = re.match(r"(\d+)\s*days?\s*(\d+)?\s*nights?", input_str)
      if match:
          days = int(match.group(1))
          return days

      match = re.match(r"(\d+)\s*ngày?", input_str)
      if match:
          days = int(match.group(1))
          return days

      match = re.match(r"(\d+)\s*days?", input_str)
      if match:
          days = int(match.group(1))
          return days

      match = re.match(r"(\d+)\s*weeks?", input_str)
      if match:
          days = int(match.group(1)) * 7
          return days
      
def get_weather(location, date_time):
    BASE_URL = "http://api.openweathermap.org/data/2.5/forecast"
    #print(f"Fetching weather for {location} on {date_time}...")

    params = {
        "q": location,
        "appid": os.environ['WEATHERMAP_API_KEY'],
        "units": "metric"
    }

    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if response.status_code == 200:
        forecasts = data['list']
        selected_forecast = min(
            forecasts,
            key=lambda x: abs(datetime.strptime(x['dt_txt'], '%Y-%m-%d %H:%M:%S') - date_time)
        )

        temperature = selected_forecast['main']['temp']
        weather_description = selected_forecast['weather'][0]['description']
        forecast_time = selected_forecast['dt_txt']
        return f"Weather in {location} on {forecast_time}: {temperature}°C, {weather_description}."
    else:
        return f"Could not fetch the weather for {location}. Error: {data.get('message', 'Unknown error')}"

