# OS-HomeTest

A production-ready support chatbot system that scrapes OptiSigns documentation, converts it to embeddings, and serves answers through an OpenAI Assistant with automated daily updates.

## Quick Start

### Prerequisites
- Python 3.11+
- Docker (for deployment)
- OpenAI API key
- Zendesk API key and email for scraping
- GitHub account (for version control and deployment)

### Local Setup

```bash
# Clone repository
git clone https://github.com/TTienMinh/OS-HomeTest.git
cd OS-HomeTest

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.sample .env
# Edit .env and add your key
```

### Running Locally

```bash
# Run the complete pipeline
python main.py

# Or run individual phases
python src/scraper.py          # Phase 1: Scrape articles
python src/vector_store.py   # Phase 2: Upload to vector store
```

## Deployment

**Last Run**: https://github.com/TTienMinh/OS-HomeTest/actions/runs/21556659446/job/62114024936

**Chunking Strategy**: Using OpenAI's auto chunking (default), which is 800 token chunks with 400 token overlap.

## OpenAI Assistant Screenshot

I cannot provide Playground screenshot because my account is not payment-bound and cannot access Playground.