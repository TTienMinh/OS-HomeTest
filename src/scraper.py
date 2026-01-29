import re
import requests
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth
from markdownify import markdownify as md

import os
from dotenv import load_dotenv
load_dotenv()

email_address = os.getenv('ZENDESK_EMAIL')
api_token = os.getenv('ZENDESK_API_TOKEN')
url = f"https://support.optisigns.com/api/v2/help_center/articles.json?per_page=40"
OUTPUT_DIR = "scraped_articles"


def scrape_articles():
    """
    Fetch articles from Zendesk Help Center API.
    """
    headers = {
        "Content-Type": "application/json",
    }

    # Use basic authentication
    auth = HTTPBasicAuth(f'{email_address}/token', api_token)

    try:
        response = requests.request(
            "GET",
            url,
            auth=auth,
            headers=headers
        )
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])
        print(f"Fetched {len(articles)} articles.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching articles: {e}")
        articles = []
    return articles


def clean_html(html_content):
    """
    Pre-process HTML before converting to Markdown.
    """
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, "html.parser")

    for irrelevant in soup.select(".ad, .navigation"):
        irrelevant.decompose()
        
    return str(soup)


def save_as_markdown(article):
    """
    Converts article HTML to Markdown and saves it.
    """
    title = article.get("title", "Untitled")
    body_html = article.get("body", "")
    html_url = article.get("html_url", "")

    # Remove special chars and replace spaces with hyphens
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title).strip().lower()
    slug = re.sub(r'[-\s]+', '-', slug)
    filename = f"{slug}.md"

    cleaned_html = clean_html(body_html)
    markdown_content = md(
        cleaned_html, 
        heading_style="ATX",  # Uses # for headings
    )

    final_content = (
        f"**Article URL:** {html_url}\n\n"
        f"# {title}\n"
        f"{markdown_content}"
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(final_content)
    
    return filename


def run_scraper():
    articles = scrape_articles()
    
    count = 0
    for article in articles:
        if article.get("draft") is True or not article.get("body"):
            continue
            
        saved_name = save_as_markdown(article)
        count += 1
        # print(f"Saved: {saved_name}")
        
    # print(f"\n--- Scraping Complete. {count} files saved to '{OUTPUT_DIR}/' ---")


if __name__ == "__main__":
    run_scraper()