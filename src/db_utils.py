import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

# Get database URL from environment
def get_db_url():
    database_url = os.getenv('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    return database_url

@contextmanager
def get_db_connection():
    """Get a database connection and cursor"""
    conn = None
    try:
        conn = psycopg2.connect(get_db_url())
        yield conn
    except Exception as e:
        print(f"Database connection error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

@contextmanager
def get_db_cursor(commit=False):
    """Get a database cursor with optional auto-commit"""
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
            if commit:
                conn.commit()
        finally:
            cursor.close()

def execute_query(query, params=None, fetch=True, commit=False):
    """Execute a database query with optional fetch and commit"""
    with get_db_cursor(commit=commit) as cursor:
        cursor.execute(query, params or ())
        if fetch:
            return cursor.fetchall()
        return None

def execute_query_single(query, params=None, commit=False):
    """Execute a query and return a single result"""
    with get_db_cursor(commit=commit) as cursor:
        cursor.execute(query, params or ())
        return cursor.fetchone()

def initialize_db():
    """Initialize the database with the schema"""
    try:
        # Read schema file
        with open('schema.sql', 'r') as f:
            schema_sql = f.read()
        
        # Execute schema
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(schema_sql)
            conn.commit()
            print("Database schema initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise
