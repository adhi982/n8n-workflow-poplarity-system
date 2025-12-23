import time
from typing import List, Dict, Any
from googleapiclient.discovery import build
from sqlalchemy.orm import Session
from app.config import settings, WORKFLOW_KEYWORDS
from app.database.models import Workflow, PopularityMetric
from .base import BaseCollector

class YouTubeCollector(BaseCollector):
    """Collector for YouTube workflow videos"""
    
    def __init__(self, db: Session):
        super().__init__(db, "youtube")
        self.youtube = build('youtube', 'v3', developerKey=settings.youtube_api_key)
    
    def collect(self, country: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Collect YouTube videos about n8n workflows"""
        workflows = []
        keywords = WORKFLOW_KEYWORDS["youtube"]
        
        try:
            self.start_collection()
            
            for keyword in keywords:
                if len(workflows) >= limit:
                    break
                
                # Search for videos
                search_response = self.youtube.search().list(
                    q=keyword,
                    part='id,snippet',
                    maxResults=min(5, limit - len(workflows)),
                    type='video',
                    regionCode=country,
                    relevanceLanguage='en'
                ).execute()
                
                video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
                
                if not video_ids:
                    continue
                
                # Get video statistics
                videos_response = self.youtube.videos().list(
                    part='statistics,snippet',
                    id=','.join(video_ids)
                ).execute()
                
                for video in videos_response.get('items', []):
                    video_data = self._process_video(video, country)
                    if video_data:
                        workflows.append(video_data)
                        self._save_workflow(video_data)
                
                # Rate limiting
                time.sleep(1)
            
            self.end_collection(len(workflows))
            
        except Exception as e:
            self.end_collection(len(workflows), str(e))
            raise
        
        return workflows
    
    def _process_video(self, video: Dict, country: str) -> Dict[str, Any]:
        """Process video data and calculate metrics"""
        try:
            stats = video['statistics']
            snippet = video['snippet']
            
            views = int(stats.get('viewCount', 0))
            likes = int(stats.get('likeCount', 0))
            comments = int(stats.get('commentCount', 0))
            
            like_ratio = round(likes / views, 6) if views > 0 else 0
            comment_ratio = round(comments / views, 6) if views > 0 else 0
            engagement = self.calculate_engagement_score(views, likes, comments)
            
            return {
                'workflow_name': snippet['title'],
                'platform': 'youtube',
                'platform_id': video['id'],
                'country': country,
                'metrics': {
                    'views': views,
                    'likes': likes,
                    'comments': comments,
                    'like_to_view_ratio': like_ratio,
                    'comment_to_view_ratio': comment_ratio,
                    'engagement_score': engagement
                }
            }
        except Exception as e:
            print(f"Error processing video: {e}")
            return None
    
    def _save_workflow(self, data: Dict[str, Any]):
        """Save workflow and metrics to database"""
        try:
            # Check if workflow exists
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
            
            # Add metrics
            metric = PopularityMetric(
                workflow_id=workflow.id,
                **data['metrics']
            )
            self.db.add(metric)
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            print(f"Error saving workflow: {e}")
