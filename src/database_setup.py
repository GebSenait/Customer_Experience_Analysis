"""
Database Setup Module
Creates PostgreSQL database and schema for bank reviews
Omega Consultancy - Task 3
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import sql
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/database_setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DatabaseSetup:
    """Handles PostgreSQL database creation and schema setup"""
    
    def __init__(
        self,
        db_name: str = 'bank_reviews',
        host: str = 'localhost',
        port: int = 5432,
        user: str = 'postgres',
        password: Optional[str] = None
    ):
        """
        Initialize database setup
        
        Args:
            db_name: Name of the database to create
            host: PostgreSQL host
            port: PostgreSQL port
            user: PostgreSQL user
            password: PostgreSQL password (if None, uses environment variable or .pgpass)
        """
        self.db_name = db_name
        self.host = host
        self.port = port
        self.user = user
        self.password = password or os.getenv('POSTGRES_PASSWORD', '')
        
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
    
    def get_connection(self, database: str = 'postgres'):
        """
        Get PostgreSQL connection
        
        Args:
            database: Database name to connect to
            
        Returns:
            psycopg2 connection object
        """
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=database
            )
            return conn
        except psycopg2.Error as e:
            error_msg = str(e)
            if "no password supplied" in error_msg.lower() or "fe_sendauth" in error_msg.lower():
                logger.error("Failed to connect to PostgreSQL: Password not provided")
                logger.error("Set password with: $env:POSTGRES_PASSWORD='your_password'")
            else:
                logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    def database_exists(self) -> bool:
        """
        Check if database exists
        
        Returns:
            True if database exists, False otherwise
        """
        try:
            conn = self.get_connection(database='postgres')
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (self.db_name,)
            )
            exists = cursor.fetchone() is not None
            
            cursor.close()
            conn.close()
            
            return exists
        except psycopg2.Error as e:
            logger.error(f"Error checking database existence: {e}")
            return False
    
    def create_database(self):
        """
        Create the bank_reviews database if it doesn't exist
        """
        if self.database_exists():
            logger.info(f"Database '{self.db_name}' already exists")
            return
        
        try:
            conn = self.get_connection(database='postgres')
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            logger.info(f"Creating database '{self.db_name}'...")
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(self.db_name)
                )
            )
            
            cursor.close()
            conn.close()
            
            logger.info(f"[OK] Database '{self.db_name}' created successfully")
        except psycopg2.Error as e:
            logger.error(f"Failed to create database: {e}")
            raise
    
    def create_schema(self, schema_file: str = 'database/schema.sql'):
        """
        Create database schema from SQL file
        
        Args:
            schema_file: Path to SQL schema file
        """
        if not os.path.exists(schema_file):
            raise FileNotFoundError(f"Schema file not found: {schema_file}")
        
        try:
            conn = self.get_connection(database=self.db_name)
            cursor = conn.cursor()
            
            logger.info(f"Reading schema from {schema_file}...")
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Execute schema SQL
            logger.info("Creating tables and indexes...")
            cursor.execute(schema_sql)
            conn.commit()
            
            # Verify tables were created
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            logger.info(f"[OK] Created tables: {', '.join(tables)}")
            
            cursor.close()
            conn.close()
            
            logger.info("✓ Schema created successfully")
        except psycopg2.Error as e:
            logger.error(f"Failed to create schema: {e}")
            if conn:
                conn.rollback()
            raise
    
    def verify_setup(self) -> dict:
        """
        Verify database setup
        
        Returns:
            Dictionary with verification results
        """
        results = {
            'database_exists': False,
            'tables_exist': False,
            'banks_count': 0,
            'reviews_count': 0
        }
        
        try:
            conn = self.get_connection(database=self.db_name)
            cursor = conn.cursor()
            
            # Check if database exists
            results['database_exists'] = True
            
            # Check tables
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('banks', 'reviews')
            """)
            table_count = cursor.fetchone()[0]
            results['tables_exist'] = (table_count == 2)
            
            # Count banks
            cursor.execute("SELECT COUNT(*) FROM banks")
            results['banks_count'] = cursor.fetchone()[0]
            
            # Count reviews
            cursor.execute("SELECT COUNT(*) FROM reviews")
            results['reviews_count'] = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            logger.info("Verification Results:")
            logger.info(f"  Database exists: {results['database_exists']}")
            logger.info(f"  Tables exist: {results['tables_exist']}")
            logger.info(f"  Banks: {results['banks_count']}")
            logger.info(f"  Reviews: {results['reviews_count']}")
            
        except psycopg2.Error as e:
            logger.error(f"Verification failed: {e}")
            results['error'] = str(e)
        
        return results
    
    def setup(self, schema_file: str = 'database/schema.sql'):
        """
        Complete database setup (create database and schema)
        
        Args:
            schema_file: Path to SQL schema file
        """
        logger.info("="*70)
        logger.info("Database Setup")
        logger.info("Omega Consultancy - Task 3")
        logger.info("="*70)
        
        try:
            # Create database
            self.create_database()
            
            # Create schema
            self.create_schema(schema_file)
            
            # Verify setup
            self.verify_setup()
            
            logger.info("="*70)
            logger.info("[OK] Database setup completed successfully")
            logger.info("="*70)
            
        except Exception as e:
            error_msg = str(e)
            if "no password supplied" in error_msg.lower() or "fe_sendauth" in error_msg.lower():
                logger.error("[ERROR] Database setup failed: PostgreSQL password not provided")
                logger.error("")
                logger.error("SOLUTION: Set the PostgreSQL password environment variable:")
                logger.error("  PowerShell: $env:POSTGRES_PASSWORD='your_password'")
                logger.error("  CMD: set POSTGRES_PASSWORD=your_password")
                logger.error("  Or use: python src/task3_main.py --password your_password")
            else:
                logger.error(f"[ERROR] Database setup failed: {e}", exc_info=True)
            raise


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup PostgreSQL database for bank reviews')
    parser.add_argument('--db-name', type=str, default='bank_reviews',
                       help='Database name (default: bank_reviews)')
    parser.add_argument('--host', type=str, default='localhost',
                       help='PostgreSQL host (default: localhost)')
    parser.add_argument('--port', type=int, default=5432,
                       help='PostgreSQL port (default: 5432)')
    parser.add_argument('--user', type=str, default='postgres',
                       help='PostgreSQL user (default: postgres)')
    parser.add_argument('--password', type=str, default=None,
                       help='PostgreSQL password (or set POSTGRES_PASSWORD env var)')
    parser.add_argument('--schema-file', type=str, default='database/schema.sql',
                       help='Path to schema SQL file')
    
    args = parser.parse_args()
    
    # Run setup
    setup = DatabaseSetup(
        db_name=args.db_name,
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password
    )
    setup.setup(schema_file=args.schema_file)


if __name__ == '__main__':
    main()

