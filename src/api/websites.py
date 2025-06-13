"""
Website Management API
"""
import os
import logging
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Path, Query, Depends
from pydantic import BaseModel, Field

from ..scrapers.site_manager import WebsiteManager
from ..scrapers.registry import ScraperRegistry

# Logger setup
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/websites",
    tags=["websites"],
    responses={404: {"description": "Not found"}},
)

# Models
class WebsiteBase(BaseModel):
    id: str
    name: str
    url: str
    description: Optional[str] = None

class WebsiteCreate(WebsiteBase):
    pass

class ScraperCreate(BaseModel):
    website_id: str
    scraper_name: str

class RunScraperRequest(BaseModel):
    website_id: str
    content_type: str = "artworks"
    pages: int = 1
    limit: int = 20
    task_name: Optional[str] = None

# Get website manager instance
def get_website_manager():
    """Create or get the website manager with registry"""
    # Ensure config directory exists
    os.makedirs('config', exist_ok=True)
    
    # Create registry with config file
    registry = ScraperRegistry(config_path='config/sites_registry.json')
    
    # Create and return website manager
    return WebsiteManager(registry=registry)

# Routes
@router.get("/", response_model=List[WebsiteBase])
async def list_websites(
    skip: int = Query(0, description="Skip first N items"),
    limit: int = Query(100, description="Limit the number of items returned"),
    website_manager: WebsiteManager = Depends(get_website_manager)
):
    """List all registered websites"""
    websites = website_manager.list_websites()
    return websites[skip:skip + limit]

@router.post("/", response_model=WebsiteBase)
async def add_website(
    website: WebsiteCreate,
    website_manager: WebsiteManager = Depends(get_website_manager)
):
    """Add a new website"""
    try:
        return website_manager.add_website(
            website_id=website.id,
            name=website.name,
            url=website.url,
            description=website.description or ""
        )
    except Exception as e:
        logger.error(f"Error adding website: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error adding website: {str(e)}")

@router.get("/{website_id}", response_model=WebsiteBase)
async def get_website(
    website_id: str = Path(..., description="Website ID"),
    website_manager: WebsiteManager = Depends(get_website_manager)
):
    """Get website details"""
    website = website_manager.get_website(website_id)
    if not website:
        raise HTTPException(status_code=404, detail=f"Website {website_id} not found")
    return website

@router.delete("/{website_id}")
async def delete_website(
    website_id: str = Path(..., description="Website ID"),
    website_manager: WebsiteManager = Depends(get_website_manager)
):
    """Delete a website"""
    success = website_manager.remove_website(website_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Website {website_id} not found")
    return {"status": "success", "message": f"Website {website_id} deleted"}

@router.get("/{website_id}/has_scraper")
async def check_scraper_exists(
    website_id: str = Path(..., description="Website ID"),
    website_manager: WebsiteManager = Depends(get_website_manager)
):
    """Check if a scraper implementation exists for the website"""
    # First check if website exists
    website = website_manager.get_website(website_id)
    if not website:
        raise HTTPException(status_code=404, detail=f"Website {website_id} not found")
        
    # Check if scraper file exists
    scraper_file = os.path.join(website_manager.sites_dir, f"{website_id}.py")
    exists = os.path.exists(scraper_file)
    
    return {
        "has_scraper": exists,
        "scraper_path": scraper_file if exists else None
    }

@router.post("/{website_id}/create_scraper")
async def create_scraper(
    scraper: ScraperCreate,
    website_manager: WebsiteManager = Depends(get_website_manager)
):
    """Create a scraper for a website"""
    try:
        # Get website details
        website = website_manager.get_website(scraper.website_id)
        if not website:
            raise HTTPException(status_code=404, detail=f"Website {scraper.website_id} not found")
            
        # Create scraper file
        file_path = website_manager.create_site_scraper(
            website_id=scraper.website_id,
            scraper_name=scraper.scraper_name,
            website_name=website.get("name"),
            website_url=website.get("url")
        )
        
        return {
            "status": "success",
            "message": f"Scraper created for website {scraper.website_id}",
            "scraper_path": file_path
        }
    except ValueError as ve:
        logger.error(f"Error creating scraper: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error creating scraper: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating scraper: {str(e)}")

@router.post("/run_scraper")
async def run_scraper(
    request: RunScraperRequest,
    website_manager: WebsiteManager = Depends(get_website_manager)
):
    """Run a website scraper"""
    try:
        # Check if website exists
        website = website_manager.get_website(request.website_id)
        if not website:
            raise HTTPException(status_code=404, detail=f"Website {request.website_id} not found")
            
        # Run the scraper
        result = website_manager.run_website_scraper(
            website_id=request.website_id,
            task_name=request.task_name,
            content_type=request.content_type,
            max_pages=request.pages,
            limit=request.limit
        )
        
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        logger.error(f"Error running scraper: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error running scraper: {str(e)}")

@router.get("/scrapers/available")
async def list_available_scrapers(
    website_manager: WebsiteManager = Depends(get_website_manager)
):
    """List all available scrapers"""
    scraper_ids = website_manager.discover_site_scrapers()
    
    # Get details for each scraper
    scrapers = []
    for scraper_id in scraper_ids:
        try:
            # Try to get website info
            website = website_manager.get_website(scraper_id)
            website_name = website.get("name") if website else scraper_id.replace("_", " ").title()
            
            # Add to list
            scrapers.append({
                "id": scraper_id,
                "name": website_name,
                "file_path": os.path.join(website_manager.sites_dir, f"{scraper_id}.py"),
                "last_modified": os.path.getmtime(os.path.join(website_manager.sites_dir, f"{scraper_id}.py"))
            })
        except Exception as e:
            logger.error(f"Error getting scraper details for {scraper_id}: {str(e)}")
    
    return scrapers 