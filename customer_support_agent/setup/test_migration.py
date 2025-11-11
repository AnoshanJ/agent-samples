"""
Quick test script to verify PostgreSQL connection and data migration.
Run this after completing the migration to ensure everything works.
"""
from db_config import get_db_connection

def test_connection():
    """Test database connection."""
    print("Testing PostgreSQL connection...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✓ Connected to PostgreSQL: {version[0][:50]}...")
        
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


def test_tables():
    """Test that all required tables exist."""
    print("\nChecking tables...")
    required_tables = [
        "flights",
        "tickets", 
        "ticket_flights",
        "boarding_passes",
        "bookings",
        "hotels",
        "car_rentals",
        "trip_recommendations"
    ]
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        print(f"Found {len(existing_tables)} tables:")
        for table in existing_tables:
            status = "✓" if table in required_tables else "?"
            print(f"  {status} {table}")
        
        missing = set(required_tables) - set(existing_tables)
        if missing:
            print(f"\n✗ Missing tables: {', '.join(missing)}")
            return False
        else:
            print("\n✓ All required tables exist")
        
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Table check failed: {e}")
        return False


def test_data():
    """Test that tables have data."""
    print("\nChecking data...")
    tables_to_check = [
        "flights",
        "tickets",
        "hotels",
        "car_rentals"
    ]
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for table in tables_to_check:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  ✓ {table}: {count:,} rows")
        
        conn.close()
        print("\n✓ Data migration successful")
        return True
    except Exception as e:
        print(f"✗ Data check failed: {e}")
        return False


def test_query():
    """Test a sample query similar to what the app uses."""
    print("\nTesting sample query...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Test query similar to search_flights
        cursor.execute("""
            SELECT flight_id, flight_no, departure_airport, arrival_airport 
            FROM flights 
            LIMIT 5
        """)
        
        results = cursor.fetchall()
        print(f"  ✓ Retrieved {len(results)} sample flights")
        
        for row in results[:3]:
            print(f"    - Flight {row[1]}: {row[2]} → {row[3]}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Query test failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("PostgreSQL Migration Verification")
    print("=" * 60)
    
    tests = [
        ("Connection", test_connection),
        ("Tables", test_tables),
        ("Data", test_data),
        ("Query", test_query)
    ]
    
    results = []
    for test_name, test_func in tests:
        results.append(test_func())
        print()
    
    print("=" * 60)
    if all(results):
        print("✅ All tests passed! Your database is ready to use.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print("=" * 60)
