#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
艺术数据爬虫 API 服务
"""

import os
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query, Path, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse

# 创建FastAPI应用
app = FastAPI(
    title="艺术数据爬虫API",
    description="提供艺术数据查询和爬虫管理的API接口",
    version="1.0.0"
)

# 配置CORS
origins = [
    "http://localhost:3000",  # 前端开发服务器
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模型定义
class ArtistBase(BaseModel):
    name: str
    country: Optional[str] = None
    birth_year: Optional[int] = None
    death_year: Optional[int] = None
    
class ArtistCreate(ArtistBase):
    pass

class Artist(ArtistBase):
    id: int
    artworks_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class ArtworkBase(BaseModel):
    title: str
    artist_id: int
    year: Optional[str] = None
    type: Optional[str] = None
    dimensions: Optional[str] = None
    image_url: Optional[str] = None
    
class ArtworkCreate(ArtworkBase):
    pass

class Artwork(ArtworkBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class ScraperTaskBase(BaseModel):
    target: str
    depth: int = 2
    concurrency: int = 2
    limit: int = 1000
    
class ScraperTaskCreate(ScraperTaskBase):
    pass

class ScraperTask(ScraperTaskBase):
    id: int
    status: str
    progress: float = 0.0
    items_scraped: int = 0
    start_time: datetime
    end_time: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class DashboardStats(BaseModel):
    artist_count: int
    artwork_count: int
    scraper_task_count: int
    data_source_count: int
    recent_data: List[Dict[str, Any]]

# 模拟数据
def get_mock_artists():
    return [
        {
            "id": 1, 
            "name": "达芬奇", 
            "country": "意大利", 
            "birth_year": 1452, 
            "death_year": 1519, 
            "artworks_count": 34,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "id": 2, 
            "name": "梵高", 
            "country": "荷兰", 
            "birth_year": 1853, 
            "death_year": 1890, 
            "artworks_count": 215,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "id": 3, 
            "name": "莫奈", 
            "country": "法国", 
            "birth_year": 1840, 
            "death_year": 1926, 
            "artworks_count": 123,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]

def get_mock_artworks():
    return [
        {
            "id": 1, 
            "title": "蒙娜丽莎", 
            "artist_id": 1, 
            "year": "1503-1519", 
            "type": "肖像画", 
            "dimensions": "77 × 53 cm", 
            "image_url": "https://placehold.co/300x400",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "id": 2, 
            "title": "最后的晚餐", 
            "artist_id": 1, 
            "year": "1495-1498", 
            "type": "壁画", 
            "dimensions": "460 × 880 cm", 
            "image_url": "https://placehold.co/300x400",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "id": 3, 
            "title": "星夜", 
            "artist_id": 2, 
            "year": "1889", 
            "type": "风景画", 
            "dimensions": "73.7 × 92.1 cm", 
            "image_url": "https://placehold.co/300x400",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "id": 4, 
            "title": "向日葵", 
            "artist_id": 2, 
            "year": "1889", 
            "type": "静物画", 
            "dimensions": "95 × 73 cm", 
            "image_url": "https://placehold.co/300x400",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]

def get_mock_tasks():
    return [
        {
            "id": 1, 
            "target": "卢浮宫官网", 
            "depth": 3, 
            "concurrency": 2, 
            "limit": 1000,
            "status": "运行中",
            "progress": 75.0,
            "items_scraped": 750,
            "start_time": datetime.now(),
            "end_time": None
        },
        {
            "id": 2, 
            "target": "大都会艺术博物馆", 
            "depth": 2, 
            "concurrency": 4, 
            "limit": 2000,
            "status": "已完成",
            "progress": 100.0,
            "items_scraped": 1863,
            "start_time": datetime.now(),
            "end_time": datetime.now()
        }
    ]

# API路由
@app.get("/")
async def root():
    return {"message": "艺术数据爬虫API服务运行中"}

# 统计数据API
@app.get("/statistics/dashboard", response_model=DashboardStats)
async def get_dashboard_statistics():
    artists = get_mock_artists()
    artworks = get_mock_artworks()
    
    return {
        "artist_count": len(artists),
        "artwork_count": len(artworks),
        "scraper_task_count": 2,
        "data_source_count": 8,
        "recent_data": [
            {"id": 1, "name": "蒙娜丽莎", "source": "卢浮宫", "type": "绘画", "createdAt": "2025-06-08 14:30:22"},
            {"id": 2, "name": "维纳斯的诞生", "source": "乌菲兹美术馆", "type": "绘画", "createdAt": "2025-06-08 13:45:10"},
            {"id": 3, "name": "最后的晚餐", "source": "圣玛丽亚修道院", "type": "壁画", "createdAt": "2025-06-08 12:10:45"}
        ]
    }

# 艺术家API
@app.get("/artists", response_model=List[Artist])
async def get_artists(
    skip: int = Query(0, description="分页起始索引"),
    limit: int = Query(100, description="每页记录数"),
    name: Optional[str] = Query(None, description="按名称搜索")
):
    artists = get_mock_artists()
    
    if name:
        artists = [a for a in artists if name.lower() in a["name"].lower()]
    
    return artists[skip:skip+limit]

@app.get("/artists/{artist_id}", response_model=Artist)
async def get_artist(
    artist_id: int = Path(..., description="艺术家ID")
):
    artists = get_mock_artists()
    for artist in artists:
        if artist["id"] == artist_id:
            return artist
    
    raise HTTPException(status_code=404, detail="艺术家不存在")

@app.get("/artists/{artist_id}/artworks", response_model=List[Artwork])
async def get_artist_artworks(
    artist_id: int = Path(..., description="艺术家ID"),
    skip: int = Query(0, description="分页起始索引"),
    limit: int = Query(100, description="每页记录数")
):
    artworks = get_mock_artworks()
    artist_artworks = [a for a in artworks if a["artist_id"] == artist_id]
    
    return artist_artworks[skip:skip+limit]

# 艺术品API
@app.get("/artworks", response_model=List[Artwork])
async def get_artworks(
    skip: int = Query(0, description="分页起始索引"),
    limit: int = Query(100, description="每页记录数"),
    title: Optional[str] = Query(None, description="按标题搜索"),
    artist_id: Optional[int] = Query(None, description="按艺术家ID筛选")
):
    artworks = get_mock_artworks()
    
    if title:
        artworks = [a for a in artworks if title.lower() in a["title"].lower()]
        
    if artist_id:
        artworks = [a for a in artworks if a["artist_id"] == artist_id]
    
    return artworks[skip:skip+limit]

@app.get("/artworks/{artwork_id}", response_model=Artwork)
async def get_artwork(
    artwork_id: int = Path(..., description="艺术品ID")
):
    artworks = get_mock_artworks()
    for artwork in artworks:
        if artwork["id"] == artwork_id:
            return artwork
    
    raise HTTPException(status_code=404, detail="艺术品不存在")

# 爬虫任务API
@app.get("/scrapers/tasks", response_model=List[ScraperTask])
async def get_scraper_tasks(
    skip: int = Query(0, description="分页起始索引"),
    limit: int = Query(100, description="每页记录数"),
    status: Optional[str] = Query(None, description="按状态筛选")
):
    tasks = get_mock_tasks()
    
    if status:
        tasks = [t for t in tasks if t["status"] == status]
    
    return tasks[skip:skip+limit]

@app.post("/scrapers/tasks", response_model=ScraperTask)
async def create_scraper_task(task: ScraperTaskCreate):
    tasks = get_mock_tasks()
    new_id = max([t["id"] for t in tasks]) + 1
    
    new_task = {
        "id": new_id,
        "target": task.target,
        "depth": task.depth,
        "concurrency": task.concurrency,
        "limit": task.limit,
        "status": "运行中",
        "progress": 0.0,
        "items_scraped": 0,
        "start_time": datetime.now(),
        "end_time": None
    }
    
    return new_task

@app.get("/scrapers/tasks/{task_id}", response_model=ScraperTask)
async def get_scraper_task(
    task_id: int = Path(..., description="任务ID")
):
    tasks = get_mock_tasks()
    for task in tasks:
        if task["id"] == task_id:
            return task
    
    raise HTTPException(status_code=404, detail="任务不存在")

@app.put("/scrapers/tasks/{task_id}/control")
async def control_scraper_task(
    task_id: int = Path(..., description="任务ID"),
    action: str = Query(..., description="控制动作：start, pause, resume, stop")
):
    valid_actions = ["start", "pause", "resume", "stop"]
    if action not in valid_actions:
        raise HTTPException(status_code=400, detail=f"无效的动作，有效值: {', '.join(valid_actions)}")
    
    tasks = get_mock_tasks()
    for task in tasks:
        if task["id"] == task_id:
            status_map = {
                "start": "运行中",
                "pause": "暂停",
                "resume": "运行中",
                "stop": "已停止"
            }
            
            return {
                "success": True,
                "message": f"任务 #{task_id} 已{status_map[action]}"
            }
    
    raise HTTPException(status_code=404, detail="任务不存在")

# 主函数
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 