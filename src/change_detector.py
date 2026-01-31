import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Set, Tuple


@dataclass
class ArticleMetadata:
    slug: str
    content_hash: str
    last_modified: str
    file_path: str
    url: str


def load_state(state_file: str = "articles_state.json") -> Dict[str, ArticleMetadata]:
    """
    Load previous state from JSON file
    """
    if not os.path.exists(state_file):
        return {}
    
    try:
        with open(state_file, 'r') as f:
            data = json.load(f)
            return {
                slug: ArticleMetadata(**meta) 
                for slug, meta in data.items()
            }
    except Exception as e:
        print(f"Error loading state: {e}")
        return {}


def save_state(state: Dict[str, ArticleMetadata], state_file: str = "articles_state.json"):
    """
    Save current state to JSON file
    """
    serializable = {
        slug: {
            'slug': meta.slug,
            'content_hash': meta.content_hash,
            'last_modified': meta.last_modified,
            'file_path': meta.file_path,
            'url': meta.url
        }
        for slug, meta in state.items()
    }
    
    with open(state_file, 'w') as f:
        json.dump(serializable, f, indent=2)


def compute_hash(content: str) -> str:
    """
    Compute SHA-256 hash of content
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def build_current_state(articles: list) -> Dict[str, ArticleMetadata]:
    """
    Build current state from articles list
    """
    current_state = {}
    
    for article in articles:
        slug = article['slug']
        content = article['markdown_content']
        content_hash = compute_hash(content)
        
        current_state[slug] = ArticleMetadata(
            slug=slug,
            content_hash=content_hash,
            last_modified=article.get('updated_at', datetime.now().isoformat()),
            file_path=f"scraped_articles/{slug}.md",
            url=article['url']
        )
    
    return current_state


def detect_changes(
    articles: list, 
    state_file: str = "articles_state.json"
) -> Tuple[Set[str], Set[str], Set[str]]:
    """
    Compare current articles with previous state
    
    Args:
        articles: List of article dictionaries
        state_file: Path to state file
    
    Returns:
        (new_slugs, updated_slugs, deleted_slugs)
    """
    previous_state = load_state(state_file)
    current_state = build_current_state(articles)
    
    current_slugs = set(current_state.keys())
    previous_slugs = set(previous_state.keys())
    
    # Detect new articles
    new_slugs = current_slugs - previous_slugs
    
    # Detect updated articles
    updated_slugs = set()
    for slug in current_slugs & previous_slugs:
        if current_state[slug].content_hash != previous_state[slug].content_hash:
            updated_slugs.add(slug)
    
    # Detect deleted articles
    deleted_slugs = previous_slugs - current_slugs
    
    # Save new state
    save_state(current_state, state_file)
    
    return new_slugs, updated_slugs, deleted_slugs


def get_changed_files(new_slugs: Set[str], updated_slugs: Set[str]) -> list:
    """
    Get list of file paths that need to be uploaded
    """
    changed_slugs = new_slugs | updated_slugs
    return [f"scraped_articles/{slug}.md" for slug in changed_slugs]


if __name__ == "__main__":
    # Example usage
    # articles = [...]  # Load or scrape articles here
    # new, updated, deleted = detect_changes(articles)
    # print("New articles:", new)
    # print("Updated articles:", updated)
    # print("Deleted articles:", deleted)
    pass