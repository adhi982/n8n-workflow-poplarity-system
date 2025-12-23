import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from app.database import SessionLocal
from app.collectors import YouTubeCollector, ForumCollector, TrendsCollector
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def collect_all_workflows():
    """Collect workflows from all platforms and countries"""
    db = SessionLocal()
    
    try:
        logger.info("Starting scheduled workflow collection...")
        
        collectors = [
            ("YouTube", YouTubeCollector),
            ("Forum", ForumCollector),
            ("Google Trends", TrendsCollector)
        ]
        
        for name, collector_class in collectors:
            for country in settings.country_list:
                try:
                    logger.info(f"Collecting {name} workflows for {country}...")
                    collector = collector_class(db)
                    workflows = collector.collect(country, settings.workflows_per_platform)
                    logger.info(f"Collected {len(workflows)} {name} workflows for {country}")
                    
                except Exception as e:
                    logger.error(f"Error collecting {name} for {country}: {e}")
        
        logger.info("Scheduled collection completed successfully")
        
    except Exception as e:
        logger.error(f"Collection job failed: {e}")
    finally:
        db.close()

def run_scheduler():
    """Run the scheduler"""
    
    if not settings.enable_scheduler:
        logger.warning("Scheduler is disabled in settings")
        return
    
    logger.info("Starting scheduler...")
    logger.info(f"Schedule: {settings.cron_schedule}")
    
    scheduler = BlockingScheduler()
    
    # Add collection job
    scheduler.add_job(
        collect_all_workflows,
        trigger=CronTrigger.from_crontab(settings.cron_schedule),
        id='collect_workflows',
        name='Collect n8n workflows from all platforms',
        replace_existing=True
    )
    
    logger.info("Scheduler started. Press Ctrl+C to exit.")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")

if __name__ == "__main__":
    run_scheduler()
