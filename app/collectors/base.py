from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.database.models import CollectionLog

class BaseCollector(ABC):
    """Base class for all data collectors"""
    
    def __init__(self, db: Session, platform: str):
        self.db = db
        self.platform = platform
        self.log_id = None
    
    def start_collection(self) -> int:
        """Log collection start"""
        log = CollectionLog(
            platform=self.platform,
            status="running",
            started_at=datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        self.log_id = log.id
        return log.id
    
    def end_collection(self, workflows_collected: int, error: str = None):
        """Log collection end"""
        if self.log_id:
            log = self.db.query(CollectionLog).filter(CollectionLog.id == self.log_id).first()
            if log:
                log.status = "failed" if error else "success"
                log.workflows_collected = workflows_collected
                log.error_message = error
                log.completed_at = datetime.utcnow()
                self.db.commit()
    
    @abstractmethod
    def collect(self, country: str, limit: int) -> List[Dict[str, Any]]:
        """Collect workflows data - must be implemented by subclasses"""
        pass
    
    def calculate_engagement_score(self, views: int, likes: int, comments: int) -> float:
        """Calculate engagement score"""
        if views == 0:
            return 0.0
        return round((likes * 2 + comments * 5) / views, 4)
