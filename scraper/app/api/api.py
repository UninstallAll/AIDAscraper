"""
Main API router
"""
from fastapi import APIRouter

from app.api.routes import auth, jobs, search, sites, users, scraped_items

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router, tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(sites.router, tags=["sites"])
api_router.include_router(jobs.router, tags=["jobs"])
api_router.include_router(search.router, tags=["search"])
api_router.include_router(scraped_items.router, tags=["scraped_items"]) 