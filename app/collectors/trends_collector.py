import time
from typing import List, Dict, Any
from pytrends.request import TrendReq
from sqlalchemy.orm import Session
from app.config import settings, WORKFLOW_KEYWORDS
from app.database.models import Workflow, PopularityMetric
from .base import BaseCollector

class TrendsCollector(BaseCollector):
    """Collector for Google Trends data"""
    
    def __init__(self, db: Session):
        super().__init__(db, "google")
        self.pytrends = TrendReq(hl='en-US', tz=360)
    
    def collect(self, country: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Collect Google Trends data for n8n workflows"""
        workflows = []
        keywords = WORKFLOW_KEYWORDS["google_trends"]
        
        try:
            self.start_collection()
            
            for keyword in keywords[:limit]:
                try:
                    # Build payload
                    self.pytrends.build_payload(
                        [keyword],
                        cat=0,
                        timeframe='today 3-m',
                        geo=country
                    )
                    
                    # Get interest over time
                    interest_df = self.pytrends.interest_over_time()
                    
                    if not interest_df.empty:
                        trend_data = self._process_trend(keyword, interest_df, country)
                        if trend_data:
                            workflows.append(trend_data)
                            self._save_workflow(trend_data)
                    
                    time.sleep(2)  # Rate limiting
                    
                except Exception as e:
                    print(f"Error collecting trend for '{keyword}': {e}")
                    continue
            
            self.end_collection(len(workflows))
            
        except Exception as e:
            self.end_collection(len(workflows), str(e))
            print(f"Trends collection error: {e}")
        
        return workflows
    
    def _process_trend(self, keyword: str, interest_df, country: str) -> Dict[str, Any]:
        """Process trend data and calculate growth"""
        try:
            values = interest_df[keyword].values
            avg_interest = int(values.mean())
            recent_interest = int(values[-7:].mean())  # Last 7 days
            older_interest = int(values[-60:-53].mean())  # 60-53 days ago
            
            # Calculate growth
            growth = 0
            if older_interest > 0:
                growth = round(((recent_interest - older_interest) / older_interest) * 100, 2)
            
            # Determine trend direction
            if growth > 20:
                trend_direction = "rising"
            elif growth < -10:
                trend_direction = "declining"
            else:
                trend_direction = "stable"
            
            # Estimate search volume (approximation based on interest)
            estimated_volume = avg_interest * 100
            
            return {
                'workflow_name': keyword,
                'platform': 'google',
                'platform_id': keyword.replace(' ', '-'),
                'country': country,
                'metrics': {
                    'views': estimated_volume,
                    'likes': 0,
                    'comments': 0,
                    'search_volume': estimated_volume,
                    'trend_direction': trend_direction,
                    'growth_percentage': growth,
                    'engagement_score': round(avg_interest / 10, 4),
                    'like_to_view_ratio': 0,
                    'comment_to_view_ratio': 0
                }
            }
        except Exception as e:
            print(f"Error processing trend: {e}")
            return None
    
    def _save_workflow(self, data: Dict[str, Any]):
        """Save workflow and metrics to database"""
        try:
            workflow = self.db.query(Workflow).filter(
                Workflow.platform == data['platform'],
                Workflow.platform_id == data['platform_id'],
                Workflow.country == data['country']
            ).first()
            
            if not workflow:
                workflow = Workflow(
                    workflow_name=data['workflow_name'],
                    platform=data['platform'],
                    platform_id=data['platform_id'],
                    country=data['country']
                )
                self.db.add(workflow)
                self.db.commit()
                self.db.refresh(workflow)
            
            metric = PopularityMetric(
                workflow_id=workflow.id,
                **data['metrics']
            )
            self.db.add(metric)
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            print(f"Error saving trends workflow: {e}")
