import os
import re
import requests
from typing import Dict, Any, List
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from markdownify import markdownify as md

load_dotenv()

ZENDESK_EMAIL = os.getenv('ZENDESK_EMAIL')
ZENDESK_API_TOKEN = os.getenv('ZENDESK_API_TOKEN')
URL = f"https://support.optisigns.com/api/v2/help_center/articles.json?per_page=40"
OUTPUT_DIR = "scraped_articles"


def scrape_articles() -> List[Dict[str, Any]]:
    """
    Fetch articles from Zendesk Help Center API.
    """
    headers = {
        "Content-Type": "application/json",
    }

    # Use basic authentication
    auth = HTTPBasicAuth(f'{ZENDESK_EMAIL}/token', ZENDESK_API_TOKEN)

    try:
        response = requests.request(
            "GET",
            URL,
            auth=auth,
            headers=headers
        )
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])
        # print(f"Fetched {len(articles)} articles.")
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


def save_as_markdown(article: Dict[str, Any], output_dir: str = OUTPUT_DIR) -> str:
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

    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(final_content)
    
    return {
        "slug": slug,
        "file_path": file_path,
        "markdown_content": final_content,
        "url": html_url
    }


def run_scraper(output_dir: str = OUTPUT_DIR) -> List[Dict[str, Any]]:
    articles = scrape_articles()
    
    saved_list = []
    for article in articles:
        if article.get("draft") is True or not article.get("body"):
            continue
            
        saved_info = save_as_markdown(article, output_dir=output_dir)
        saved_list.append(saved_info)

        # print(f"Saved: {saved_info['slug']}")

    return saved_list


if __name__ == "__main__":
    run_scraper()