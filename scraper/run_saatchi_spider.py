"""
SaatchiArt Spider Runner
"""
import json
import logging
import os
import sys
import traceback
from datetime import datetime

# Add project root directory to Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.db.database import SessionLocal, engine
from app import models
from app.models.scraped_item import ScrapedItem
from app.scrapers.spider_factory import SpiderFactory
from app.models.site import SiteConfig

# Scrapy imports for running the spider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def ensure_database_tables():
    """
    Ensure database tables are created
    """
    try:
        # Create tables
        models.Base.metadata.create_all(bind=engine)
        logger.info("Database tables created")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        logger.error(traceback.format_exc())


def create_saatchi_site_config(db):
    """
    Create SaatchiArt site configuration
    
    Args:
        db: Database session
        
    Returns:
        SiteConfig: Site configuration object
    """
    try:
        # Load configuration
        config_file = 'app/scrapers/spiders/saatchi_art_config.json'
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Check if already exists
        site = db.query(models.SiteConfig).filter(
            models.SiteConfig.name == config['name'],
            models.SiteConfig.tenant_id == 'test'
        ).first()
        
        if site:
            logger.info(f"Site configuration already exists: {site.name}")
            return site
        
        # Create site configuration
        site = models.SiteConfig(
            name=config['name'],
            url=config['url'],
            description=config.get('description', ''),
            requires_login=config.get('requires_login', False),
            login_url=config.get('login_url', ''),
            login_username_field=config.get('login_username_field', ''),
            login_password_field=config.get('login_password_field', ''),
            login_username=config.get('login_username', ''),
            login_password=config.get('login_password', ''),
            start_urls=config.get('start_urls', [config['url']]),
            allowed_domains=config.get('allowed_domains', []),
            list_page_xpath=config.get('list_page_xpath', ''),
            next_page_xpath=config.get('next_page_xpath', ''),
            detail_page_xpath=config.get('detail_page_xpath', ''),
            field_mappings=config.get('field_mappings', {}),
            use_playwright=config.get('use_playwright', True),
            config=config.get('config', {}),
            tenant_id='test',
            is_active=True
        )
        
        db.add(site)
        db.commit()
        db.refresh(site)
        
        logger.info(f"Site configuration created: {site.name}")
        return site
    except Exception as e:
        logger.error(f"Error creating site configuration: {e}")
        logger.error(traceback.format_exc())
        return None


def create_test_job(db, site_config):
    """
    Create test job
    
    Args:
        db: Database session
        site_config: Site configuration object
        
    Returns:
        Job: Job object
    """
    try:
        # Create job
        job = models.Job(
            name=f"{site_config.name} Test Job",
            site_config_id=site_config.id,
            config={},
            status="pending",
            progress=0,
            items_scraped=0,
            items_saved=0,
            schedule_type="once",
            tenant_id='test'
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        logger.info(f"Job created: {job.name}")
        return job
    except Exception as e:
        logger.error(f"Error creating test job: {e}")
        logger.error(traceback.format_exc())
        return None


def run_spider(spider):
    """
    Run a spider using CrawlerProcess
    
    Args:
        spider: Spider instance
    """
    try:
        # Create crawler process
        process = CrawlerProcess(get_project_settings())
        
        # Add spider to process
        process.crawl(spider.__class__, **{
            'site_config': spider.site_config,
            'job_id': spider.job_id,
            '_job_logger': spider.logger
        })
        
        # Start crawling (non-blocking)
        process.start(stop_after_crawl=True)
        
        return True
    except Exception as e:
        logger.error(f"Error running spider with CrawlerProcess: {e}")
        logger.error(traceback.format_exc())
        return False


def run_saatchi_spider():
    """
    Run SaatchiArt spider
    """
    # Ensure database tables are created
    ensure_database_tables()
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Create site configuration
        site_config = create_saatchi_site_config(db)
        if not site_config:
            logger.error("Failed to create site configuration, exiting")
            return
        
        # Create test job
        job = create_test_job(db, site_config)
        if not job:
            logger.error("Failed to create test job, exiting")
            return
        
        # Update job status to running
        job.status = "running"
        job.started_at = datetime.now()
        db.commit()
        
        try:
            # Create spider
            spider = SpiderFactory.create_spider(site_config=site_config, job_id=job.id)
            
            # Run spider
            logger.info(f"Starting spider: {spider.name}")
            success = run_spider(spider)
            
            if success:
                # Check scraped items
                items = db.query(ScrapedItem).filter(ScrapedItem.job_id == job.id).all()
                logger.info(f"Total items scraped: {len(items)}")
                
                # Update job status to completed
                job.status = "completed"
                job.progress = 100
                job.completed_at = datetime.now()
                job.items_scraped = len(items)
                job.items_saved = len(items)
                db.commit()
                
                logger.info("Spider run completed")
            else:
                # Update job status to failed
                job.status = "failed"
                job.completed_at = datetime.now()
                job.error = "Failed to run spider"
                db.commit()
                logger.info("Job marked as failed")
                
        except Exception as e:
            # Log error but continue execution
            logger.error(f"Error running spider: {e}")
            logger.error(traceback.format_exc())
            
            # Update job status to failed
            job.status = "failed"
            job.completed_at = datetime.now()
            job.error = str(e)
            db.commit()
            logger.info("Job marked as failed")
            
    except Exception as e:
        logger.error(f"Error in run_saatchi_spider: {e}")
        logger.error(traceback.format_exc())
    finally:
        db.close()


if __name__ == '__main__':
    try:
        run_saatchi_spider()
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        logger.error(traceback.format_exc()) 