# AIDA Scraper

A comprehensive SaaS platform for collecting and analyzing information about artists and curators across the web.

## Overview

AIDA Scraper is designed to help researchers, galleries, and educational institutions gather and analyze art-related data from across the internet. The platform offers:

- Automated web scraping of art websites using Scrapy and Playwright
- NLP-driven information extraction and classification
- Structured data storage and search capabilities
- Visualization of artist-curator-institution relationships
- Multi-tenant architecture for team-based research

## Quick Start

### One-Click Startup

To start all components with a single command:

```
start_all.bat
```

This will:
1. Initialize the database
2. Start the API server
3. Start the Celery worker
4. Run a test spider for SaatchiArt

### Stop All Services

To stop all running components:

```
stop_all.bat
```

## Manual Setup

### Prerequisites

- Python 3.8+
- PostgreSQL (optional, SQLite is used by default)
- Redis (for Celery task queue)

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r scraper/requirements.txt
   ```

### Running Components Individually

1. Initialize the database:
   ```
   cd scraper
   python start.py --init-db
   ```

2. Start the API server:
   ```
   cd scraper
   python start.py --start-api
   ```

3. Start the Celery worker:
   ```
   cd scraper
   python start_worker.py
   ```

4. Run a spider:
   ```
   cd scraper
   python run_saatchi_spider.py
   ```

## API Documentation

Once the API server is running, you can access the documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Architecture

AIDA Scraper follows a modular architecture:

- **API Layer**: FastAPI for high-performance REST endpoints
- **Scraper Layer**: Scrapy + Playwright for handling JavaScript-rendered sites
- **Processing Layer**: NLP pipelines for text analysis
- **Storage Layer**: PostgreSQL/SQLite for structured data, Elasticsearch for search
- **Task Queue**: Celery + Redis for asynchronous job processing

## Spiders

The following spiders are currently implemented:

- **SaatchiArt**: Scrapes artists and artworks from SaatchiArt
- **Artsy**: Scrapes artists, exhibitions, and artworks from Artsy
- **WikiArt**: Scrapes artists, artworks, and genres from WikiArt
- **ArtGallery**: Generic spider for art gallery websites

## Configuration

Configuration is managed through JSON files in `scraper/app/scrapers/spiders/`.

Example configuration:

```json
{
  "name": "SaatchiArt",
  "url": "https://www.saatchiart.com",
  "description": "Scrape artists and artworks from SaatchiArt website",
  "requires_login": false,
  "start_urls": [
    "https://www.saatchiart.com/artists",
    "https://www.saatchiart.com/paintings"
  ],
  "allowed_domains": [
    "www.saatchiart.com",
    "saatchiart.com"
  ],
  "use_playwright": true,
  "config": {
    "max_pages": 2,
    "max_items_per_category": 20
  }
}
```

## License

MIT 