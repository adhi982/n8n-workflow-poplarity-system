from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Numeric, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Workflow(Base):
    __tablename__ = "workflows"
    
    id = Column(BigInteger, primary_key=True, index=True)
    workflow_name = Column(String(500), nullable=False)
    platform = Column(String(50), nullable=False, index=True)
    platform_id = Column(String(255))
    country = Column(String(10), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    metrics = relationship("PopularityMetric", back_populates="workflow", cascade="all, delete-orphan")

class PopularityMetric(Base):
    __tablename__ = "popularity_metrics"
    
    id = Column(BigInteger, primary_key=True, index=True)
    workflow_id = Column(BigInteger, ForeignKey("workflows.id", ondelete="CASCADE"))
    
    # Common metrics
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    
    # Calculated ratios
    like_to_view_ratio = Column(Numeric(10, 6))
    comment_to_view_ratio = Column(Numeric(10, 6))
    engagement_score = Column(Numeric(10, 4), index=True)
    
    # Platform-specific
    replies = Column(Integer, nullable=True)
    participants = Column(Integer, nullable=True)
    search_volume = Column(Integer, nullable=True)
    trend_direction = Column(String(20), nullable=True)
    growth_percentage = Column(Numeric(10, 2), nullable=True)
    
    collected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationship
    workflow = relationship("Workflow", back_populates="metrics")

class CollectionLog(Base):
    __tablename__ = "collection_logs"
    
    id = Column(BigInteger, primary_key=True, index=True)
    platform = Column(String(50), nullable=False, index=True)
    status = Column(String(20), nullable=False)
    workflows_collected = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
