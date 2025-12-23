import sys
import uvicorn
from app.config import settings

def main():
    """Main application runner"""
    
    if "--scheduler-only" in sys.argv:
        # Run scheduler only (implemented in Phase 5)
        from app.scheduler import run_scheduler
        run_scheduler()
    else:
        # Run API server
        uvicorn.run(
            "app.main:app",
            host=settings.api_host,
            port=settings.api_port,
            reload=settings.debug
        )

if __name__ == "__main__":
    main()
