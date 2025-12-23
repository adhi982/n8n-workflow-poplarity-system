from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class PopularityMetricsResponse(BaseModel):
    """Response model for popularity metrics"""
    views: int
    likes: int
    comments: int
    like_to_view_ratio: float
    comment_to_view_ratio: float
    engagement_score: Optional[float] = None
    replies: Optional[int] = None
    participants: Optional[int] = None
    search_volume: Optional[int] = None
    trend_direction: Optional[str] = None
    growth_percentage: Optional[float] = None
    
    class Config:
        from_attributes = True

class WorkflowResponse(BaseModel):
    """Response model for a single workflow"""
    workflow: str
    platform: str
    popularity_metrics: PopularityMetricsResponse
    country: str
    collected_at: datetime
    
    class Config:
        from_attributes = True

class WorkflowListResponse(BaseModel):
    """Response model for list of workflows"""
    total: int
    limit: int
    offset: int
    workflows: List[WorkflowResponse]

class StatsResponse(BaseModel):
    """Response model for statistics"""
    total_workflows: int
    by_platform: dict
    by_country: dict
    last_updated: datetime
    collection_status: dict

class CollectRequest(BaseModel):
    """Request model for manual collection"""
    platforms: List[str] = Field(default=["youtube", "forum", "google"])
    countries: List[str] = Field(default=["US", "IN"])

class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    database: str
    timestamp: datetime
