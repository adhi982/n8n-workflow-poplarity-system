# API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
No authentication required for read endpoints. All endpoints are currently public.

---

## Endpoints

### 1. Root Endpoint
**GET /**

Returns API information and available endpoints.

**Response:**
```json
{
  "message": "n8n Workflow Popularity System API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/api/v1/health"
}
```

---

### 2. Health Check
**GET /api/v1/health**

Check API and database connectivity status.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-12-23T10:30:00.000000"
}
```

**Status Codes:**
- 200: Service healthy
- 500: Service unhealthy

---

### 3. Get All Workflows
**GET /api/v1/workflows**

Retrieve workflows with pagination and filtering.

**Query Parameters:**
- `platform` (optional): Filter by platform (`youtube`, `forum`, `google`)
- `country` (optional): Filter by country (`US`, `IN`)
- `limit` (default: 50, max: 100): Number of results per page
- `offset` (default: 0): Pagination offset
- `sort_by` (default: `engagement_score`): Sort field
- `order` (default: `desc`): Sort order (`asc`, `desc`)

**Example Request:**
```bash
GET /api/v1/workflows?platform=youtube&country=US&limit=10
```

**Response:**
```json
{
  "total": 150,
  "limit": 10,
  "offset": 0,
  "workflows": [
    {
      "workflow": "Build Agents INSTANTLY with n8n",
      "platform": "youtube",
      "popularity_metrics": {
        "views": 12500,
        "likes": 630,
        "comments": 88,
        "like_to_view_ratio": 0.05,
        "comment_to_view_ratio": 0.007,
        "engagement_score": 1.234,
        "replies": null,
        "participants": null,
        "search_volume": null,
        "trend_direction": null,
        "growth_percentage": null
      },
      "country": "US",
      "collected_at": "2025-12-23T10:30:00.000000"
    }
  ]
}
```

**Status Codes:**
- 200: Success
- 400: Invalid parameters
- 500: Server error

---

### 4. Get Workflows by Platform
**GET /api/v1/workflows/{platform}**

Get workflows from a specific platform.

**Path Parameters:**
- `platform`: Platform name (`youtube`, `forum`, `google`)

**Query Parameters:**
- `country` (optional): Filter by country
- `limit` (default: 50): Number of results
- `offset` (default: 0): Pagination offset

**Example Request:**
```bash
GET /api/v1/workflows/youtube?country=US&limit=20
```

**Response:** Same format as Get All Workflows

**Status Codes:**
- 200: Success
- 404: Platform not found
- 500: Server error

---

### 5. Get Trending Workflows
**GET /api/v1/workflows/trending**

Get trending workflows sorted by engagement score.

**Query Parameters:**
- `country` (optional): Filter by country
- `limit` (default: 20, max: 100): Number of results

**Example Request:**
```bash
GET /api/v1/workflows/trending?limit=10
```

**Response:** Same format as Get All Workflows, sorted by engagement_score DESC

**Status Codes:**
- 200: Success
- 500: Server error

---

### 6. Get Statistics
**GET /api/v1/workflows/stats**

Get aggregated statistics about collected workflows.

**Response:**
```json
{
  "total_workflows": 150,
  "by_platform": {
    "youtube": 60,
    "forum": 50,
    "google": 40
  },
  "by_country": {
    "US": 75,
    "IN": 75
  },
  "last_updated": "2025-12-23T10:30:00.000000",
  "collection_status": {
    "youtube": "success",
    "forum": "failed",
    "google": "success"
  }
}
```

**Status Codes:**
- 200: Success
- 500: Server error

---

### 7. Trigger Data Collection
**POST /api/v1/collect**

Manually trigger workflow data collection.

**Request Body:**
```json
{
  "platforms": ["youtube", "forum", "google"],
  "countries": ["US", "IN"]
}
```

**Default Values:**
- `platforms`: ["youtube", "forum", "google"]
- `countries`: ["US", "IN"]

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/collect \
  -H "Content-Type: application/json" \
  -d '{"platforms": ["youtube"], "countries": ["US"]}'
```

**Response:**
```json
{
  "status": "completed",
  "results": [
    {
      "platform": "youtube",
      "country": "US",
      "workflows_collected": 20,
      "status": "success"
    }
  ]
}
```

**Status Codes:**
- 200: Collection completed
- 400: Invalid request body
- 500: Collection failed

---

## Data Models

### Workflow Response
```json
{
  "workflow": "string",
  "platform": "youtube | forum | google",
  "popularity_metrics": {
    "views": "integer",
    "likes": "integer",
    "comments": "integer",
    "like_to_view_ratio": "float",
    "comment_to_view_ratio": "float",
    "engagement_score": "float",
    "replies": "integer | null",
    "participants": "integer | null",
    "search_volume": "integer | null",
    "trend_direction": "string | null",
    "growth_percentage": "float | null"
  },
  "country": "US | IN",
  "collected_at": "datetime"
}
```

### Platform-Specific Metrics

**YouTube:**
- `views`: Video view count
- `likes`: Video like count
- `comments`: Video comment count
- `engagement_score`: Calculated as (likes * 2 + comments * 5) / views

**Forum (Discourse):**
- `views`: Topic view count
- `likes`: Topic like count
- `comments`: Number of posts
- `replies`: Reply count
- `participants`: Unique participant count
- `engagement_score`: (views * 0.1 + likes * 5 + replies * 3 + participants * 2) / 100

**Google Trends:**
- `search_volume`: Estimated search volume
- `trend_direction`: "rising", "stable", or "declining"
- `growth_percentage`: Growth percentage over last 60 days
- `engagement_score`: Average interest / 10

---

## Rate Limits

- YouTube API: 10,000 units/day (configured in environment)
- Discourse API: 60 requests/minute (configured in environment)
- Google Trends: No official limit, 2-second delay between requests

---

## Error Responses

All endpoints return errors in the following format:

```json
{
  "detail": "Error message description"
}
```

**Common Status Codes:**
- 400: Bad Request - Invalid parameters
- 404: Not Found - Resource not found
- 422: Validation Error - Request body validation failed
- 500: Internal Server Error - Server-side error

---

## Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Both interfaces allow you to:
- View all endpoints
- See request/response schemas
- Test endpoints directly
- View example requests and responses

---

## Examples

### Example 1: Get Top 10 YouTube Workflows

```bash
curl -X GET "http://localhost:8000/api/v1/workflows?platform=youtube&limit=10&sort_by=engagement_score&order=desc"
```

### Example 2: Get US Trending Workflows

```bash
curl -X GET "http://localhost:8000/api/v1/workflows/trending?country=US&limit=20"
```

### Example 3: Trigger YouTube Collection

```bash
curl -X POST "http://localhost:8000/api/v1/collect" \
  -H "Content-Type: application/json" \
  -d '{"platforms": ["youtube"], "countries": ["US", "IN"]}'
```

### Example 4: Get Statistics

```bash
curl -X GET "http://localhost:8000/api/v1/workflows/stats"
```

### Example 5: Health Check

```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

---

## Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Get trending workflows
response = requests.get(f"{BASE_URL}/api/v1/workflows/trending?limit=10")
workflows = response.json()

for workflow in workflows['workflows']:
    print(f"{workflow['platform']}: {workflow['workflow']}")
    print(f"  Engagement Score: {workflow['popularity_metrics']['engagement_score']}")
    print(f"  Views: {workflow['popularity_metrics']['views']}")
    print()

# Trigger collection
response = requests.post(
    f"{BASE_URL}/api/v1/collect",
    json={"platforms": ["youtube"], "countries": ["US"]}
)
print(response.json())
```

---

## JavaScript/Node.js Client Example

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000';

// Get all workflows
async function getWorkflows() {
  try {
    const response = await axios.get(`${BASE_URL}/api/v1/workflows`, {
      params: {
        platform: 'youtube',
        limit: 20,
        country: 'US'
      }
    });
    console.log(response.data);
  } catch (error) {
    console.error('Error:', error.response.data);
  }
}

// Trigger collection
async function triggerCollection() {
  try {
    const response = await axios.post(`${BASE_URL}/api/v1/collect`, {
      platforms: ['youtube'],
      countries: ['US']
    });
    console.log(response.data);
  } catch (error) {
    console.error('Error:', error.response.data);
  }
}

getWorkflows();
```

---

## Notes

- All timestamps are in UTC
- Pagination is zero-indexed (offset starts at 0)
- Maximum limit per request is 100
- Engagement scores are calculated differently per platform
- Forum collection requires API credentials (optional)
- Collection can take several minutes depending on rate limits
