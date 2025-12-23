# n8n Workflow Popularity System

A production-ready system that identifies and tracks the most popular n8n workflows across multiple platforms (YouTube, n8n Forum, Google Trends) with measurable popularity evidence.

## Features

- Collect workflow data from YouTube, n8n Community Forum, and Google Trends
- Track popularity metrics: views, likes, comments, engagement ratios
- REST API for accessing workflow data
- Automated data collection via cron scheduler
- Country-specific segmentation (US, India)
- Supabase PostgreSQL database integration

## Quick Start

### 1. Clone Repository

```bash
git clone <repository-url>
cd n8n-workflow-popularity-system
```

### 2. Setup Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your credentials
# - Supabase credentials
# - YouTube API key
# - Discourse API credentials (optional)
```

### 4. Setup Supabase Database

1. Create a Supabase project at https://supabase.com
2. Go to SQL Editor in Supabase Dashboard
3. Run the database migration script from database.sql
4. Copy your project URL and keys to `.env` file

### 5. Run Application

```bash
# Start API server
python run.py

# In another terminal, start scheduler
python run.py --scheduler-only
```

### 6. Access API

- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/health

## API Endpoints

### GET /api/v1/workflows

Get all workflows with pagination and filtering

Query Parameters:

- `platform` (optional): youtube, forum, google
- `country` (optional): US, IN
- `limit` (default: 50): Results per page
- `offset` (default: 0): Pagination offset

### GET /api/v1/workflows/

Get workflows from specific platform

### GET /api/v1/workflows/trending

Get trending workflows (highest engagement)

### GET /api/v1/workflows/stats

Get aggregated statistics

### POST /api/v1/collect

Manually trigger data collection

Request Body:

```json
{
  "platforms": ["youtube", "forum", "google"],
  "countries": ["US", "IN"]
}
```

### GET /api/v1/health

Health check endpoint

## Project Structure

```
n8n-workflow-popularity-system/
├── app/
│   ├── api/              # API routes and models
│   ├── collectors/       # Data collectors
│   ├── config/           # Configuration management
│   ├── database/         # Database models and connection
│   └── scheduler/        # Cron job scheduler
├── tests/                # Test files
├── .env                  # Environment variables (not in git)
├── .env.example          # Example environment file
├── requirements.txt      # Python dependencies
└── run.py               # Application runner
```

## Environment Variables

See `.env.example` for all available configuration options.

Required:

- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_SERVICE_KEY`: Supabase service role key
- `DATABASE_URL`: PostgreSQL connection string
- `YOUTUBE_API_KEY`: YouTube Data API v3 key

Optional:

- `DISCOURSE_API_KEY`: n8n Forum API key
- `DISCOURSE_API_USERNAME`: n8n Forum username

## Development

### Run Tests

```bash
# Test database connection
python test_db_connection.py

# Test collectors
python test_collectors.py

# Test complete system
python test_complete_system.py
```

### API Development

FastAPI automatically generates interactive API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
