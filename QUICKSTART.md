# Quick Start Guide

## For Developers

### Minimal Setup (5 minutes)

```powershell
# 1. Setup environment
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure credentials
cp .env.example .env
# Edit .env with your Supabase and YouTube API credentials

# 3. Test connection
python test_db_connection.py

# 4. Start API
python run.py
```

Visit: http://localhost:8000/docs

### First API Call

```bash
# Check health
curl http://localhost:8000/api/v1/health

# Collect workflows
curl -X POST http://localhost:8000/api/v1/collect

# View workflows
curl http://localhost:8000/api/v1/workflows
```

---

## For Testers

### Test Individual Components

```powershell
# Test database
python test_db_connection.py

# Test data collectors
python test_collectors.py

# Test complete system (requires API running)
python test_complete_system.py
```

### Manual Testing Checklist

- [ ] API health endpoint responds
- [ ] Can collect YouTube workflows
- [ ] Can collect Google Trends data
- [ ] Workflows appear in database
- [ ] Statistics endpoint shows data
- [ ] Trending endpoint works
- [ ] Pagination works correctly
- [ ] Platform filtering works
- [ ] Country filtering works

---

## Common Tasks

### Change Collection Schedule

Edit `.env`:

```bash
# Daily at 2 AM (default)
CRON_SCHEDULE=0 2 * * *

# Every 6 hours
CRON_SCHEDULE=0 */6 * * *

# Every Monday at 3 AM
CRON_SCHEDULE=0 3 * * 1
```

### Add More Countries

Edit `.env`:

```bash
COUNTRIES=US,IN,GB,DE,FR
```

### Increase Workflows Per Platform

Edit `.env`:

```bash
WORKFLOWS_PER_PLATFORM=50
```

### Run Manual Collection

```powershell
python -c "from app.scheduler import collect_all_workflows; collect_all_workflows()"
```

---

## Troubleshooting

### Database Connection Issues

Special characters in password? URL encode them:

- `!` → `%21`
- `@` → `%40`
- `#` → `%23`

### YouTube API Errors

- Check API key is valid
- Verify YouTube Data API v3 is enabled
- Check quota not exceeded (10,000 units/day)

### Service Won't Start

- Check port 8000 is available
- Verify virtual environment activated
- Ensure all dependencies installed
- Check `.env` file exists and configured

---

## Next Steps

1. Read [README.md](README.md) for full documentation
2. Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API detailsrt

- Check logs for errors
- Review documentation files
- Test individual components
- Verify environment configuration
