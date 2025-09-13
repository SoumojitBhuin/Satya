import requests
import os

def google_search_with_api(query: str, api_key: str, search_engine_id: str, num_results: int = 3) -> list:
    """
    Performs a Google search using the official Custom Search JSON API.

    Args:
        query (str): The search term.
        api_key (str): Your Google API key.
        search_engine_id (str): Your Programmable Search Engine ID (CX).
        num_results (int): The number of results to return (max 10 per request).
        refinement_label (str, optional): The refinement label to trigger (e.g., 'news').

    Returns:
        list: A list of URL strings, or an empty list if an error occurs.
    """
    url = "https://www.googleapis.com/customsearch/v1"
    
    params = {
        'q': query,
        'key': api_key,
        'cx': search_engine_id,
        'num': num_results
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        search_results = response.json()
        urls = [item['link'] for item in search_results.get('items', [])]
        print(urls)
        return urls
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
        return []
    except KeyError:
        print("Error: Could not find 'items' in the API response. No results?")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []

# --- Example Usage ---
if __name__ == "__main__":
    # PLEASE DELETE YOUR OLD KEY AND USE A NEW ONE
    MY_API_KEY = "AIzaSyDDvVGlu46XN-QLK-bmbMCDeaideSeTtCA"
    MY_SEARCH_ENGINE_ID = "03770eece84864b6b"

    if MY_API_KEY == "YOUR_NEW_API_KEY":
        print("ERROR: Please replace with your actual new API key.")
    else:
        search_title = "Deadly Gen Z protests in Nepal have prompted calls for a new government and an Indian airlift for its stranded citizens"
        
        # Get the top 3 URLs using the 'news' refinement
        reference_url = google_search_with_api(
            query=search_title,
            api_key=MY_API_KEY,
            search_engine_id=MY_SEARCH_ENGINE_ID,
            num_results=3
        )
        
        if top_news_urls:
            print("\n--- Top 3 News URLs Found ---")
            for i, url in enumerate(top_news_urls, 1):
                print(f"{i}. {url}")
        else:
            print("\nCould not retrieve search results.")