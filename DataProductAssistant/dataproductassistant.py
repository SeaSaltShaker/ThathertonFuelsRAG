import os
import requests
import base64
import configparser

config = configparser.ConfigParser()

API_KEY = config['DEFAULT'][apiKey]

ENDPOINT = config['DEFAULT']['modelEndpoint']


headers = {
    "Content-Type": "application/json",
    "api-key": API_KEY,
}

# Payload for the request
payload = {
  "messages": [
    {
      "role": "system",
      "content": [
        {
          "type": "text",
          "text": "You are an AI assistant that helps people find information."
        }
      ]
    },
        {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Where should I go for a vacation?"
        }
      ]
    }
  ],
  "temperature": 0.7,
  "top_p": 0.95,
  "max_tokens": 800
}


# Send request
try:
    response = requests.post(ENDPOINT, headers=headers, json=payload)
    response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
except requests.RequestException as e:
    raise SystemExit(f"Failed to make the request. Error: {e}")

# Handle the response as needed (e.g., print or process)
output = response.json().get("choices")[0].get("message").get("content")

print(output)

