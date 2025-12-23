from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional, List
from datetime import datetime
from app.database import get_db
from app.database.models import Workflow, PopularityMetric, CollectionLog
from app.collectors import YouTubeCollector, ForumCollector, TrendsCollector
from app.config import settings
from .models import (
    WorkflowResponse, WorkflowListResponse, StatsResponse,
    CollectRequest, HealthResponse, PopularityMetricsResponse
)

router = APIRouter(prefix="/api/v1", tags=["workflows"])

@router.get("/workflows", response_model=WorkflowListResponse)
def get_workflows(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    country: Optional[str] = Query(None, description="Filter by country"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("engagement_score", description="Sort field"),
    order: str = Query("desc", description="Sort order"),
    db: Session = Depends(get_db)
):
    """Get all workflows with pagination and filtering"""
    
    # Build query
    query = db.query(Workflow, PopularityMetric).join(PopularityMetric)
    
    if platform:
        query = query.filter(Workflow.platform == platform)
    if country:
        query = query.filter(Workflow.country == country)
    
    # Get total count
    total = query.count()
    
    # Apply sorting
    sort_column = getattr(PopularityMetric, sort_by, PopularityMetric.engagement_score)
    if order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)
    
    # Apply pagination
    results = query.offset(offset).limit(limit).all()
    
    # Format response
    workflows = []
    for workflow, metric in results:
        workflows.append({
            "workflow": workflow.workflow_name,
            "platform": workflow.platform,
            "popularity_metrics": metric,
            "country": workflow.country,
            "collected_at": metric.collected_at
        })
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "workflows": workflows
    }

@router.get("/workflows/{platform}", response_model=WorkflowListResponse)
def get_workflows_by_platform(
    platform: str,
    country: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get workflows from specific platform"""
    return get_workflows(platform=platform, country=country, limit=limit, offset=offset, db=db)

@router.get("/workflows/trending", response_model=WorkflowListResponse)
def get_trending_workflows(
    country: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get trending workflows (highest engagement)"""
    return get_workflows(
        country=country,
        limit=limit,
        offset=0,
        sort_by="engagement_score",
        order="desc",
        db=db
    )

@router.get("/workflows/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """Get aggregated statistics"""
    
    # Total workflows
    total = db.query(Workflow).count()
    
    # By platform
    by_platform = {}
    platform_counts = db.query(
        Workflow.platform,
        func.count(Workflow.id)
    ).group_by(Workflow.platform).all()
    
    for platform, count in platform_counts:
        by_platform[platform] = count
    
    # By country
    by_country = {}
    country_counts = db.query(
        Workflow.country,
        func.count(Workflow.id)
    ).group_by(Workflow.country).all()
    
    for country, count in country_counts:
        by_country[country] = count
    
    # Last updated
    last_metric = db.query(PopularityMetric).order_by(
        desc(PopularityMetric.collected_at)
    ).first()
    last_updated = last_metric.collected_at if last_metric else datetime.utcnow()
    
    # Collection status
    collection_status = {}
    for platform in ["youtube", "forum", "google"]:
        last_log = db.query(CollectionLog).filter(
            CollectionLog.platform == platform
        ).order_by(desc(CollectionLog.created_at)).first()
        
        collection_status[platform] = last_log.status if last_log else "unknown"
    
    return {
        "total_workflows": total,
        "by_platform": by_platform,
        "by_country": by_country,
        "last_updated": last_updated,
        "collection_status": collection_status
    }

@router.post("/collect")
def trigger_collection(
    request: CollectRequest,
    db: Session = Depends(get_db)
):
    """Manually trigger data collection"""
    
    collectors = {
        "youtube": YouTubeCollector,
        "forum": ForumCollector,
        "google": TrendsCollector
    }
    
    results = []
    
    for platform in request.platforms:
        if platform not in collectors:
            continue
        
        collector_class = collectors[platform]
        
        for country in request.countries:
            try:
                collector = collector_class(db)
                workflows = collector.collect(country, settings.workflows_per_platform)
                results.append({
                    "platform": platform,
                    "country": country,
                    "workflows_collected": len(workflows),
                    "status": "success"
                })
            except Exception as e:
                results.append({
                    "platform": platform,
                    "country": country,
                    "workflows_collected": 0,
                    "status": "failed",
                    "error": str(e)
                })
    
    return {
        "status": "completed",
        "results": results
    }

@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "connected"
    except:
        db_status = "disconnected"
    
    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status,
        "timestamp": datetime.utcnow()
    }
