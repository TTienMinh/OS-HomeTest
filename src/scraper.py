import requests
from requests.auth import HTTPBasicAuth

import os
from dotenv import load_dotenv
load_dotenv()


def scrape_articles():
    url = f"https://support.optisigns.com/api/v2/help_center/articles.json?per_page=30"

    headers = {
        "Content-Type": "application/json",
    }
    email_address = os.getenv('ZENDESK_EMAIL')
    api_token = os.getenv('ZENDESK_API_TOKEN')
    # Use basic authentication
    auth = HTTPBasicAuth(f'{email_address}/token', api_token)

    response = requests.request(
        "GET",
        url,
        auth=auth,
        headers=headers
    )
    return response


if __name__ == "__main__":
    response = scrape_articles()
    if response.status_code != 200:
        print(f"Failed to fetch articles. Status code: {response.status_code}")
        exit(1)
    else:
        data = response.json()
        articles = data.get("articles", [])
        print(f"Successfully fetched {len(articles)} articles.")

        for article in articles:
            print(f"ID: {article['id']}, Title: {article['title']}")