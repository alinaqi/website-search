# perplexity_client.py
from openai import OpenAI
import os
import requests

# Initialize Perplexity client using environment variable for the API key
perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
client = OpenAI(api_key=perplexity_api_key, base_url="https://api.perplexity.ai")

url = "https://api.perplexity.ai/chat/completions"

def get_perplexity_response(messages, search_website, model="llama-3-sonar-large-32k-online"):
    """
    Makes a request to the Perplexity API to generate a response for the provided messages.

    Args:
        messages (list): List of messages in the format required by the Perplexity API.
        search_website (str): Domain to filter the search.
        model (str): The model to use for generating the response.

    Returns:
        dict: The response from the Perplexity API in a JSON-serializable format.
    """
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
        "top_p": 0.9,
        "return_citations": True,
        "search_domain_filter": [f"{search_website}"],
        "return_images": False,
        "return_related_questions": False,
        "search_recency_filter": "month",
        "top_k": 0,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 1
    }

    headers = {
        "Authorization": f"Bearer {perplexity_api_key}",
        "Content-Type": "application/json"
    }

    try:
        # Make a POST request to the Perplexity API
        response = requests.post(url, json=payload, headers=headers)

        # Raise an exception if the request was unsuccessful
        response.raise_for_status()

        # Convert the response to JSON format
        response_data = response.json()

        # Print the raw response for debugging purposes
        print("Perplexity API Response:", response_data)

        # Convert the response object to a JSON-serializable dictionary
        serialized_response = {
            "id": response_data.get("id"),
            "object": response_data.get("object"),
            "created": response_data.get("created"),
            "model": response_data.get("model"),
            "choices": [
                {
                    "index": choice.get("index"),
                    "message": choice.get("message"),
                    "finish_reason": choice.get("finish_reason")
                } for choice in response_data.get("choices", [])
            ]
        }

        return response_data

    except requests.exceptions.RequestException as e:
        print(f"Error calling Perplexity API: {e}")
        return {"error": str(e)}