#!/usr/bin/env python3
"""
Quick Start Script for PostgreSQL Migration
This interactive script helps you set up and migrate to PostgreSQL.
"""
import os
import sys
from pathlib import Path

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_step(number, text):
    print(f"\n[Step {number}] {text}")
    print("-" * 70)

def check_env_file():
    """Check if .env file exists."""
    env_path = Path(".env")
    if env_path.exists():
        print("✓ .env file found")
        return True
    else:
        print("✗ .env file not found")
        return False

def create_env_file():
    """Interactive .env file creation."""
    print("\nLet's create your .env file...")
    print("\nYou'll need:")
    print("1. A PostgreSQL connection string from Neon or Supabase")
    print("2. An OpenAI API key")
    print("3. A Tavily API key")
    
    proceed = input("\nDo you have all the required information? (y/n): ")
    if proceed.lower() != 'y':
        print("\nPlease gather the following:")
        print("• Neon: Sign up at https://neon.tech and create a project")
        print("• Supabase: Sign up at https://supabase.com and create a project")
        print("• OpenAI: Get API key from https://platform.openai.com/api-keys")
        print("• Tavily: Get API key from https://tavily.com")
        return False
    
    print("\n")
    database_url = input("Enter your PostgreSQL connection string: ").strip()
    openai_key = input("Enter your OpenAI API key: ").strip()
    tavily_key = input("Enter your Tavily API key: ").strip()
    
    env_content = f"""# OpenAI API Key
OPENAI_API_KEY={openai_key}

# Tavily API Key (for web search)
TAVILY_API_KEY={tavily_key}

# PostgreSQL Database Configuration
DATABASE_URL={database_url}
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("\n✓ .env file created successfully!")
    return True

def check_dependencies():
    """Check if required packages are installed."""
    print("\nChecking dependencies...")
    required = {
        'sqlalchemy': 'sqlalchemy',
        'psycopg2': 'psycopg2',
        'pandas': 'pandas',
        'requests': 'requests',
        'dotenv': 'python-dotenv'
    }
    
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n✗ Missing packages: {', '.join(missing)}")
        install = input("\nWould you like to install them now? (y/n): ")
        if install.lower() == 'y':
            import subprocess
            cmd = [sys.executable, "-m", "pip", "install"] + missing
            subprocess.run(cmd)
            print("\n✓ Dependencies installed")
            return True
        return False
    else:
        print("\n✓ All dependencies installed")
        return True

def run_migration():
    """Run the migration script."""
    print("\nRunning migration script...")
    print("This will:")
    print("1. Download the SQLite database")
    print("2. Update dates to current time")
    print("3. Migrate all data to PostgreSQL")
    
    proceed = input("\nProceed with migration? (y/n): ")
    if proceed.lower() != 'y':
        return False
    
    print("\n")
    os.chdir("setup")
    
    try:
        import migrate_to_postgres
        os.chdir("..")
        print("\n✓ Migration completed successfully!")
        return True
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        os.chdir("..")
        return False

def run_tests():
    """Run verification tests."""
    print("\nRunning verification tests...")
    
    os.chdir("setup")
    try:
        import test_migration
        os.chdir("..")
        return True
    except Exception as e:
        print(f"\n✗ Tests failed: {e}")
        os.chdir("..")
        return False

def main():
    print_header("PostgreSQL Migration Quick Start")
    print("This script will help you migrate from SQLite to PostgreSQL")
    print("using either Neon or Supabase as your database provider.")
    
    # Step 1: Check/create .env file
    print_step(1, "Checking Environment Configuration")
    if not check_env_file():
        if not create_env_file():
            print("\n❌ Setup cancelled. Please create .env file manually.")
            print("   See .env.example for reference.")
            return
    
    # Step 2: Check dependencies
    print_step(2, "Checking Dependencies")
    if not check_dependencies():
        print("\n❌ Please install missing dependencies:")
        print("   pip install -r requirements.txt")
        return
    
    # Step 3: Test database connection
    print_step(3, "Testing Database Connection")
    try:
        from setup.db_config import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✓ Connected to PostgreSQL")
        print(f"  Version: {version[:60]}...")
        conn.close()
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("\nPlease check your DATABASE_URL in .env file")
        print("It should look like:")
        print("  postgresql://user:password@host:port/database?sslmode=require")
        return
    
    # Step 4: Run migration
    print_step(4, "Migrating Data")
    if not run_migration():
        print("\n❌ Migration failed. Please check the error above.")
        return
    
    # Step 5: Run tests
    print_step(5, "Verifying Migration")
    run_tests()
    
    # Final message
    print_header("Setup Complete!")
    print("Your database has been successfully migrated to PostgreSQL!")
    print("\nNext steps:")
    print("1. Start your application: python main.py")
    print("2. Test the API at: http://localhost:8091/invocations")
    print("\nFor more information:")
    print("• Read MIGRATION_GUIDE.md for detailed documentation")
    print("• Read MIGRATION_SUMMARY.md for technical details")
    print("\n✨ Happy coding! ✨\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        print("Please check the error and try again")
