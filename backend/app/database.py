# -*- coding: utf-8 -*-
"""
Database configuration and connection
"""
import os
import sys
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Ensure stdout uses utf-8 encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Detect database type
IS_SQLITE = settings.DATABASE_URL.startswith("sqlite")

# Create engine with appropriate settings
if IS_SQLITE:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    print("[INFO] Using SQLite database")
else:
    # PostgreSQL configuration
    try:
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        
        def get_db_params():
            """Parse DATABASE_URL and return connection parameters"""
            db_url = settings.DATABASE_URL
            parts = db_url.replace("postgresql://", "").split("@")
            user_pass = parts[0].split(":")
            host_port_db = parts[1].split("/")
            host_port = host_port_db[0].split(":")
            
            return {
                "user": user_pass[0],
                "password": user_pass[1],
                "host": host_port[0],
                "port": int(host_port[1]) if len(host_port) > 1 else 5432,
                "database": host_port_db[1]
            }
        
        def create_database_if_not_exists():
            """Create database if it doesn't exist"""
            db_params = get_db_params()
            database_name = db_params.pop("database")
            
            try:
                conn = psycopg2.connect(
                    host=db_params["host"],
                    port=db_params["port"],
                    user=db_params["user"],
                    password=db_params["password"],
                    database="postgres"
                )
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                cursor = conn.cursor()
                
                cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{database_name}'")
                exists = cursor.fetchone()
                
                if not exists:
                    cursor.execute(f'CREATE DATABASE "{database_name}"')
                    print(f"[OK] Database '{database_name}' created successfully")
                else:
                    print(f"[OK] Database '{database_name}' already exists")
                
                cursor.close()
                conn.close()
            except Exception as e:
                print(f"[ERROR] Could not connect to PostgreSQL: {e}")
        
        create_database_if_not_exists()
    except ImportError:
        print("[WARNING] psycopg2 not installed, skipping PostgreSQL setup")
    
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )
    print("[INFO] Using PostgreSQL database")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    from app import models  # Import models to register them
    Base.metadata.create_all(bind=engine)
    print("[OK] Database tables created successfully")