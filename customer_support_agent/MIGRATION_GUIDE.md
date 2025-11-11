# PostgreSQL Migration Guide

This guide will help you migrate from SQLite to PostgreSQL using either Neon or Supabase.

## Prerequisites

- Python 3.11 or higher
- An account on either [Neon](https://neon.tech) or [Supabase](https://supabase.com)

## Step 1: Create a PostgreSQL Database

### Option A: Using Neon (Recommended for simplicity)

1. Go to [neon.tech](https://neon.tech) and sign up/login
2. Click "Create a project"
3. Choose a project name and region
4. Copy the connection string (it will look like):
   ```
   postgresql://user:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require
   ```

### Option B: Using Supabase

1. Go to [supabase.com](https://supabase.com) and sign up/login
2. Click "New project"
3. Fill in project details and wait for setup to complete
4. Go to Project Settings > Database
5. Copy the connection string (under "Connection string" > "URI"):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```

## Step 2: Configure Environment Variables

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your database connection string:
   ```env
   DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require
   ```

3. Also add your OpenAI and Tavily API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```

## Step 3: Install Dependencies

Make sure all required packages are installed:

```bash
pip install -r requirements.txt
```

The key packages for PostgreSQL are:
- `sqlalchemy` - Database toolkit
- `psycopg2-binary` - PostgreSQL adapter

## Step 4: Run the Migration Script

Execute the migration script to transfer data from SQLite to PostgreSQL:

```bash
cd setup
python migrate_to_postgres.py
```

This script will:
1. Download the SQLite database (if not already present)
2. Update dates to current time
3. Connect to your PostgreSQL database
4. Migrate all tables and data
5. Confirm successful migration

## Step 5: Verify the Migration

You can verify the migration by:

1. **Using Neon Console**: Go to your Neon project and use the SQL Editor to run:
   ```sql
   SELECT table_name FROM information_schema.tables 
   WHERE table_schema = 'public';
   ```

2. **Using Supabase Dashboard**: Go to Table Editor to see all migrated tables

3. **Using Python**: Run a quick test:
   ```python
   from setup.db_config import get_db_connection
   
   conn = get_db_connection()
   cursor = conn.cursor()
   cursor.execute("SELECT COUNT(*) FROM flights")
   print(f"Number of flights: {cursor.fetchone()[0]}")
   conn.close()
   ```

## Step 6: Run the Application

Start the application as usual:

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn app:app --host 0.0.0.0 --port 8091
```

## Expected Tables

After migration, you should have the following tables:
- `flights`
- `tickets`
- `ticket_flights`
- `boarding_passes`
- `bookings`
- `hotels`
- `car_rentals`
- `trip_recommendations`

## Troubleshooting

### Connection Issues

If you get connection errors:

1. **Check SSL requirement**: Neon and Supabase require SSL. Make sure your connection string includes `?sslmode=require`

2. **Verify credentials**: Double-check your username, password, and host in the connection string

3. **Check firewall**: Ensure your IP is allowed (Neon and Supabase free tiers usually allow all IPs)

### Migration Errors

If migration fails:

1. **Check database is empty**: If tables already exist, you may need to drop them first
2. **Verify permissions**: Ensure your database user has CREATE TABLE privileges
3. **Check logs**: Look at the error message for specific issues

### Running the App

If the app fails to start:

1. **Verify .env file**: Make sure DATABASE_URL is set correctly
2. **Test connection manually**: Use the verification script above
3. **Check imports**: Ensure all tool files can import `setup.db_config`

## Key Changes Made

The migration involved:

1. **Database Configuration** (`setup/db_config.py`):
   - Created centralized database connection management
   - Added support for environment variables
   - Ensured SSL connections for Neon/Supabase

2. **Migration Script** (`setup/migrate_to_postgres.py`):
   - Downloads and processes SQLite data
   - Transfers all tables to PostgreSQL
   - Updates timestamps to current date

3. **Tool Files** (all `tools/*.py` files):
   - Replaced `sqlite3.connect(db)` with `get_db_connection()`
   - Changed SQL placeholder from `?` to `%s` (PostgreSQL syntax)
   - Updated imports to use `setup.db_config`

## Benefits of PostgreSQL

- **Remote Access**: Access your database from anywhere
- **Scalability**: Better performance for concurrent users
- **ACID Compliance**: Better data integrity
- **Advanced Features**: Full-text search, JSON support, etc.
- **Free Tier**: Both Neon and Supabase offer generous free tiers

## Cost Considerations

### Neon Free Tier
- 0.5 GB storage
- Unlimited projects
- Auto-suspend after inactivity

### Supabase Free Tier
- 500 MB database space
- 2 GB bandwidth
- Unlimited API requests

Both are sufficient for development and testing!
