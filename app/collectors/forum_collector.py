import time
import requests
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.config import settings, WORKFLOW_KEYWORDS
from app.database.models import Workflow, PopularityMetric
from .base import BaseCollector

class ForumCollector(BaseCollector):
    """Collector for n8n community forum posts"""
    
    BASE_URL = "https://community.n8n.io"
    
    def __init__(self, db: Session):
        super().__init__(db, "forum")
        self.headers = {
            'Api-Key': settings.discourse_api_key,
            'Api-Username': settings.discourse_api_username
        } if settings.discourse_api_key else {}
    
    def collect(self, country: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Collect popular forum posts"""
        workflows = []
        
        try:
            self.start_collection()
            
            # Get latest topics
            response = requests.get(
                f"{self.BASE_URL}/latest.json",
                headers=self.headers,
                params={'per_page': limit}
            )
            response.raise_for_status()
            
            topics = response.json().get('topic_list', {}).get('topics', [])
            
            for topic in topics[:limit]:
                topic_data = self._process_topic(topic, country)
                if topic_data:
                    workflows.append(topic_data)
                    self._save_workflow(topic_data)
                
                time.sleep(0.5)
            
            self.end_collection(len(workflows))
            
        except Exception as e:
            self.end_collection(len(workflows), str(e))
            print(f"Forum collection error: {e}")
        
        return workflows
    
    def _process_topic(self, topic: Dict, country: str) -> Dict[str, Any]:
        """Process forum topic data"""
        try:
            views = topic.get('views', 0)
            likes = topic.get('like_count', 0)
            replies = topic.get('reply_count', 0)
            posts = topic.get('posts_count', 0)
            participants = topic.get('participant_count', 0) or topic.get('posters_count', 1)
            
            # Calculate engagement
            engagement = (views * 0.1 + likes * 5 + replies * 3 + participants * 2) / 100
            
            return {
                'workflow_name': topic['title'],
                'platform': 'forum',
                'platform_id': str(topic['id']),
                'country': country,
                'metrics': {
                    'views': views,
                    'likes': likes,
                    'comments': posts,
                    'replies': replies,
                    'participants': participants,
                    'like_to_view_ratio': round(likes / views, 6) if views > 0 else 0,
                    'comment_to_view_ratio': round(posts / views, 6) if views > 0 else 0,
                    'engagement_score': round(engagement, 4)
                }
            }
        except Exception as e:
            print(f"Error processing topic: {e}")
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
            print(f"Error saving forum workflow: {e}")
