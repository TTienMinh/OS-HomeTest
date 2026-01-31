# main.py
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
from src.scraper import run_scraper
from src.change_detector import detect_changes, get_changed_files
from src.vector_store import run_vector_store_setup

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
vector_store_id = os.getenv('VECTOR_STORE_ID')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('scraper.log')
    ]
)
logger = logging.getLogger(__name__)


def main():
    """
    Daily job execution:
    1. Re-scrape all articles
    2. Detect changes
    3. Upload only delta
    4. Log results
    """
    start_time = datetime.now()
    logger.info(f"Starting daily scrape job at {start_time.isoformat()}")

    if not openai_api_key:
        logger.error("OPENAI_API_KEY not set")
        sys.exit(1)
    
    if not vector_store_id:
        logger.error("VECTOR_STORE_ID not set")
        sys.exit(1)
    
    try:
        # Step 1: Re-scrape all articles
        logger.info("\n--- Scraping Articles ---")
        articles = run_scraper(limit=40)
        logging.info(f"Total articles scraped and saved: {len(articles)}")
        
        # Step 2: Detect changes
        logger.info("\n--- Detecting Changes ---")
        new_slugs, updated_slugs, deleted_slugs = detect_changes(articles, state_file="articles_state.json")
    
        logger.info(f"New articles: {len(new_slugs)}")
        logger.info(f"Updated articles: {len(updated_slugs)}")
        logger.info(f"Deleted articles: {len(deleted_slugs)}")
        
        if new_slugs:
            logger.info(f"  New: {', '.join(list(new_slugs)[:5])}{'...' if len(new_slugs) > 5 else ''}")
        if updated_slugs:
            logger.info(f"  Updated: {', '.join(list(updated_slugs)[:5])}{'...' if len(updated_slugs) > 5 else ''}")
        if deleted_slugs:
            logger.info(f"  Deleted: {', '.join(list(deleted_slugs)[:5])}{'...' if len(deleted_slugs) > 5 else ''}")
        
        # Step 3: Upload delta to vector store
        logger.info("\n--- Uploading Delta ---")
        changed_files = get_changed_files(new_slugs, updated_slugs)
        
        if changed_files:
            stats = run_vector_store_setup(changed_files)
            
            logger.info("\n=== UPLOAD SUMMARY ===")
            logger.info(f"Files added: {len(new_slugs)}")
            logger.info(f"Files updated: {len(updated_slugs)}")
            logger.info(f"Files skipped: {len(articles) - len(changed_files)}")
            logger.info(f"Upload status: {stats['status']}")
            logger.info(f"OpenAI upload stats: {stats}")
        else:
            logger.info("No changes detected - skipping upload")
            logger.info(f"Total files unchanged: {len(articles)}")
        
        # Step 4: Execution summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("\nJOB COMPLETE")
        logger.info(f"Start time: {start_time.isoformat()}")
        logger.info(f"End time: {end_time.isoformat()}")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Total articles: {len(articles)}")
        logger.info(f"New: {len(new_slugs)} | Updated: {len(updated_slugs)} | Deleted: {len(deleted_slugs)} | Unchanged: {len(articles) - len(changed_files)}")
        
        # Exit with success
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"\nJOB FAILED!")
        logger.error(f"Error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()