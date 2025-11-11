# PostgreSQL Migration - Architecture Overview

## Before (SQLite)

```
┌─────────────────────────────────────────────────────────────┐
│                     Customer Support Agent                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Flights    │    │    Hotels    │    │  Car Rentals │  │
│  │    Tool      │    │     Tool     │    │     Tool     │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │                    │                    │          │
│         │  import sqlite3    │  import sqlite3    │          │
│         │  from . import db  │  from . import db  │          │
│         └────────────────────┴────────────────────┘          │
│                              │                                │
│                              ▼                                │
│                    ┌──────────────────┐                      │
│                    │ tools/__init__.py │                     │
│                    │ db="travel2.sqlite"│                    │
│                    └──────────────────┘                      │
│                              │                                │
│                              ▼                                │
│                    ┌──────────────────┐                      │
│                    │  travel2.sqlite  │                      │
│                    │  (Local File)    │                      │
│                    └──────────────────┘                      │
└─────────────────────────────────────────────────────────────┘

Issues:
❌ Local only - can't access from other machines
❌ Not suitable for production deployment
❌ No concurrent access handling
❌ Manual file management
```

## After (PostgreSQL)

```
┌─────────────────────────────────────────────────────────────┐
│                     Customer Support Agent                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Flights    │    │    Hotels    │    │  Car Rentals │  │
│  │    Tool      │    │     Tool     │    │     Tool     │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │                    │                    │          │
│         │  from setup.db_config import           │          │
│         │         get_db_connection               │          │
│         └────────────────────┴────────────────────┘          │
│                              │                                │
│                              ▼                                │
│                   ┌────────────────────┐                     │
│                   │ setup/db_config.py │                     │
│                   │  get_db_connection()│                    │
│                   │  create_db_engine() │                    │
│                   └─────────┬──────────┘                     │
│                             │                                 │
│                             │ reads DATABASE_URL              │
│                             ▼                                 │
│                      ┌─────────────┐                         │
│                      │  .env file  │                         │
│                      │ DATABASE_URL│                         │
│                      └─────────────┘                         │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               │ SSL Connection
                               ▼
          ┌────────────────────────────────────────┐
          │       Cloud PostgreSQL Database        │
          ├────────────────────────────────────────┤
          │                                        │
          │  Option A: Neon                       │
          │  ┌──────────────────────────────────┐ │
          │  │ • Serverless PostgreSQL          │ │
          │  │ • Auto-scaling                   │ │
          │  │ • 0.5GB free tier                │ │
          │  │ • Auto-suspend when idle         │ │
          │  └──────────────────────────────────┘ │
          │                                        │
          │  Option B: Supabase                   │
          │  ┌──────────────────────────────────┐ │
          │  │ • PostgreSQL + extras            │ │
          │  │ • Built-in authentication        │ │
          │  │ • 500MB free tier                │ │
          │  │ • Real-time subscriptions        │ │
          │  └──────────────────────────────────┘ │
          │                                        │
          └────────────────────────────────────────┘

Benefits:
✅ Remote access from anywhere
✅ Production-ready deployment
✅ Handles concurrent users
✅ Automatic backups
✅ Better performance & scalability
✅ Free tier available
```

## Migration Flow

```
┌────────────────────────────────────────────────────────────┐
│                    Migration Process                       │
└────────────────────────────────────────────────────────────┘

Step 1: Download SQLite Database
┌─────────────────────────────────┐
│ Google Cloud Storage            │
│ travel2.sqlite                  │
└───────────┬─────────────────────┘
            │
            ▼
Step 2: Update Dates & Process
┌─────────────────────────────────┐
│ migrate_to_postgres.py          │
│ • Update timestamps             │
│ • Clean NULL values             │
│ • Prepare data                  │
└───────────┬─────────────────────┘
            │
            ▼
Step 3: Transfer to PostgreSQL
┌─────────────────────────────────┐
│ Upload all tables:              │
│ • flights                       │
│ • tickets                       │
│ • ticket_flights                │
│ • boarding_passes               │
│ • bookings                      │
│ • hotels                        │
│ • car_rentals                   │
│ • trip_recommendations          │
└───────────┬─────────────────────┘
            │
            ▼
Step 4: Verify Migration
┌─────────────────────────────────┐
│ test_migration.py               │
│ ✓ Connection test               │
│ ✓ Table check                   │
│ ✓ Data verification             │
│ ✓ Query test                    │
└─────────────────────────────────┘
```

## Code Changes Summary

### Database Connection Pattern

**Before:**
```python
# In every tool file
import sqlite3
from . import db

def some_tool_function():
    conn = sqlite3.connect(db)  # Connect to local file
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM table WHERE id = ?", (id,))
    results = cursor.fetchall()
    conn.close()
```

**After:**
```python
# In every tool file
from setup.db_config import get_db_connection

def some_tool_function():
    conn = get_db_connection()  # Connect to remote PostgreSQL
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM table WHERE id = %s", (id,))
    results = cursor.fetchall()
    conn.close()
```

### SQL Syntax Changes

| Operation | SQLite | PostgreSQL |
|-----------|--------|------------|
| Parameter | `?` | `%s` |
| String match | `LIKE ?` | `LIKE %s` |
| Date format | String | Timestamp |
| Boolean | 0/1 | true/false |

## File Structure

```
customer_support_agent/
├── .env                          # ⭐ NEW: Environment config
├── .env.example                  # ⭐ NEW: Template
├── README.md                     # ✏️ UPDATED: Added PostgreSQL info
├── MIGRATION_GUIDE.md            # ⭐ NEW: Detailed guide
├── MIGRATION_SUMMARY.md          # ⭐ NEW: Technical summary
├── ARCHITECTURE.md               # ⭐ NEW: This file
├── app.py
├── main.py
├── requirements.txt              # (sqlalchemy, psycopg2 already present)
│
├── setup/
│   ├── db.py                     # (Original SQLite setup)
│   ├── db_config.py              # ⭐ NEW: PostgreSQL connection
│   ├── migrate_to_postgres.py   # ⭐ NEW: Migration script
│   ├── test_migration.py        # ⭐ NEW: Verification script
│   └── quick_start.py           # ⭐ NEW: Interactive setup
│
├── tools/
│   ├── __init__.py              # ✏️ UPDATED: Import db_config
│   ├── flights.py               # ✏️ UPDATED: Use PostgreSQL
│   ├── hotels.py                # ✏️ UPDATED: Use PostgreSQL
│   ├── car_rentals.py           # ✏️ UPDATED: Use PostgreSQL
│   ├── excursions.py            # ✏️ UPDATED: Use PostgreSQL
│   └── policies.py              # (No changes needed)
│
└── agent/
    ├── agent.py                 # (No changes needed)
    ├── state.py                 # (No changes needed)
    └── utils.py                 # (No changes needed)

Legend:
⭐ NEW - Files added
✏️ UPDATED - Files modified
```

## Environment Variables

```env
# Required for AI functionality
OPENAI_API_KEY=sk-proj-...
TAVILY_API_KEY=tvly-...

# Database Configuration
# Choose ONE of these patterns:

# Pattern 1: Full connection string (Recommended)
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require

# Pattern 2: Individual components
# DB_HOST=ep-xxx.region.aws.neon.tech
# DB_NAME=dbname
# DB_USER=username
# DB_PASSWORD=password
# DB_PORT=5432
```

## Quick Start Commands

```bash
# 1. Interactive setup (easiest)
python setup/quick_start.py

# 2. Manual setup
cp .env.example .env
# Edit .env with your credentials
python setup/migrate_to_postgres.py
python setup/test_migration.py

# 3. Run the application
python main.py

# 4. Test the API
curl -X POST http://localhost:8091/invocations \
  -H "Content-Type: application/json" \
  -d '{
    "thread_id": 1,
    "question": "Show me available flights",
    "passenger_id": "3442 587242"
  }'
```

## Troubleshooting Decision Tree

```
Can't connect to database?
├─ Check DATABASE_URL in .env
├─ Verify SSL mode: ?sslmode=require
├─ Test credentials in database provider's console
└─ Check firewall rules

Migration fails?
├─ Check internet connection (downloads SQLite DB)
├─ Verify database is empty or drop existing tables
├─ Ensure CREATE TABLE permissions
└─ Check Python version (3.10+ required)

Import errors?
├─ Install requirements: pip install -r requirements.txt
├─ Check Python environment is activated
└─ Verify PYTHONPATH includes project root

App won't start?
├─ Check all environment variables are set
├─ Verify database migration completed
├─ Check port 8091 is available
└─ Review error logs for specific issues
```

## Performance Considerations

| Aspect | SQLite | PostgreSQL |
|--------|--------|------------|
| Concurrent users | ❌ Limited | ✅ Excellent |
| Network latency | ✅ None (local) | ⚠️ ~10-50ms |
| Query optimization | ⚠️ Basic | ✅ Advanced |
| Caching | Manual | Built-in |
| Connection pooling | N/A | Supported |
| Backup/restore | Manual file | Automated |
| Scaling | ❌ Single file | ✅ Cloud scaling |

## Security Enhancements

With PostgreSQL:
- ✅ SSL/TLS encrypted connections
- ✅ Role-based access control
- ✅ Audit logging available
- ✅ IP whitelist filtering
- ✅ Password policies
- ✅ Automatic security updates (managed services)

## Cost Analysis

### Free Tier Comparison

| Provider | Storage | Compute | Bandwidth | Limits |
|----------|---------|---------|-----------|--------|
| **Neon** | 0.5 GB | Unlimited | Unlimited | Auto-suspend, 1 project |
| **Supabase** | 500 MB | 2 GB egress | 2 GB/month | 50,000 rows |
| **SQLite** | Local disk | Local CPU | N/A | Hardware dependent |

Both Neon and Supabase are sufficient for development and moderate production use!

## Future Enhancements

Possible improvements now that you're on PostgreSQL:

1. **Full-Text Search**: Use PostgreSQL's built-in FTS
2. **JSON Columns**: Store flexible data structures
3. **Materialized Views**: Cache complex queries
4. **Partitioning**: Manage large datasets efficiently
5. **Replication**: Set up read replicas
6. **PostGIS**: Add geospatial capabilities
7. **Connection Pooling**: Use PgBouncer for better performance
8. **Monitoring**: Set up metrics and alerts

---

**Ready to migrate?** Start with `python setup/quick_start.py` 🚀
