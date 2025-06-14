"""
Scraped items API routes
"""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.db.database import get_db

router = APIRouter()


@router.get("/scraped-items", response_model=List[schemas.ScrapedItem])
def read_scraped_items(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    job_id: int = Query(None, description="Filter by job ID"),
    item_type: str = Query(None, description="Filter by item type"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve scraped items.
    """
    # Get scraped items for the current user's tenant
    items = services.scraped_item.get_multi(
        db, 
        skip=skip, 
        limit=limit, 
        tenant_id=current_user.tenant_id,
        job_id=job_id,
        item_type=item_type
    )
    return items


@router.get("/scraped-items/{item_id}", response_model=schemas.ScrapedItem)
def read_scraped_item(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get specific scraped item by ID.
    """
    item = services.scraped_item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Scraped item not found")
    
    # Check if the item belongs to the user's tenant
    if item.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return item


@router.delete("/scraped-items/{item_id}", response_model=schemas.ScrapedItem)
def delete_scraped_item(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a scraped item.
    """
    item = services.scraped_item.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Scraped item not found")
    
    item = services.scraped_item.remove(db, id=item_id)
    return item 