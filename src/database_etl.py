"""
Database ETL Module
Extract, Transform, and Load review data into PostgreSQL
Omega Consultancy - Task 3
"""

import os
import sys
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from typing import Optional, Dict, List
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/database_etl.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DatabaseETL:
    """Handles ETL operations for bank reviews data"""
    
    def __init__(
        self,
        db_name: str = 'bank_reviews',
        host: str = 'localhost',
        port: int = 5432,
        user: str = 'postgres',
        password: Optional[str] = None,
        batch_size: int = 1000
    ):
        """
        Initialize ETL pipeline
        
        Args:
            db_name: Database name
            host: PostgreSQL host
            port: PostgreSQL port
            user: PostgreSQL user
            password: PostgreSQL password
            batch_size: Batch size for inserts
        """
        self.db_name = db_name
        self.host = host
        self.port = port
        self.user = user
        self.password = password or os.getenv('POSTGRES_PASSWORD', '')
        self.batch_size = batch_size
        
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
    
    def get_connection(self):
        """
        Get PostgreSQL connection
        
        Returns:
            psycopg2 connection object
        """
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.db_name
            )
            return conn
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    def get_bank_mapping(self) -> Dict[str, int]:
        """
        Get mapping of bank names to bank_ids
        
        Returns:
            Dictionary mapping bank_name to bank_id
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT bank_id, bank_name FROM banks")
        mapping = {row[1]: row[0] for row in cursor.fetchall()}
        
        cursor.close()
        conn.close()
        
        logger.info(f"Loaded bank mapping: {mapping}")
        return mapping
    
    def load_data(self, input_file: Optional[str] = None) -> pd.DataFrame:
        """
        Load review data from CSV file
        
        Args:
            input_file: Path to CSV file (if None, uses most recent processed file)
            
        Returns:
            DataFrame with review data
        """
        if input_file is None:
            # Find most recent processed file
            processed_dir = 'data/processed'
            if not os.path.exists(processed_dir):
                raise FileNotFoundError(f"Processed data directory not found: {processed_dir}")
            
            csv_files = [f for f in os.listdir(processed_dir) if f.endswith('.csv')]
            if not csv_files:
                raise FileNotFoundError(f"No CSV files found in {processed_dir}")
            
            input_file = os.path.join(processed_dir, sorted(csv_files)[-1])
            logger.info(f"Using most recent processed file: {input_file}")
        
        # Load CSV
        df = pd.read_csv(input_file)
        logger.info(f"Loaded {len(df)} reviews from {input_file}")
        
        # Check required columns
        required_columns = ['review', 'rating', 'date', 'bank']
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        
        return df
    
    def load_task2_data(self, input_file: Optional[str] = None) -> pd.DataFrame:
        """
        Load Task 2 analyzed data (with sentiment) if available
        
        Args:
            input_file: Path to Task 2 CSV file (if None, searches in data/analyzed)
            
        Returns:
            DataFrame with sentiment data, or None if not found
        """
        if input_file is None:
            # Check for Task 2 analyzed data
            analyzed_dir = 'data/analyzed'
            if not os.path.exists(analyzed_dir):
                logger.info("Task 2 analyzed data directory not found, using Task 1 data only")
                return None
            
            csv_files = [f for f in os.listdir(analyzed_dir) 
                        if f.startswith('sentiment_thematic_analysis_') and f.endswith('.csv')]
            if not csv_files:
                logger.info("No Task 2 analyzed data found, using Task 1 data only")
                return None
            
            input_file = os.path.join(analyzed_dir, sorted(csv_files)[-1])
            logger.info(f"Found Task 2 data: {input_file}")
        
        try:
            df = pd.read_csv(input_file)
            logger.info(f"Loaded {len(df)} reviews with sentiment data")
            return df
        except Exception as e:
            logger.warning(f"Could not load Task 2 data: {e}")
            return None
    
    def transform_data(self, df: pd.DataFrame, bank_mapping: Dict[str, int], 
                       task2_df: Optional[pd.DataFrame] = None) -> List[tuple]:
        """
        Transform DataFrame to database-ready format
        
        Args:
            df: DataFrame with review data
            bank_mapping: Mapping of bank_name to bank_id
            task2_df: Optional DataFrame with Task 2 sentiment data
            
        Returns:
            List of tuples ready for database insertion
        """
        records = []
        
        # Merge Task 2 data if available
        if task2_df is not None:
            # Try to merge on review text and date
            if 'review_text' in task2_df.columns:
                task2_df = task2_df.rename(columns={'review_text': 'review'})
            
            # Merge on review and date
            merge_cols = ['review', 'date']
            if all(col in df.columns and col in task2_df.columns for col in merge_cols):
                df = df.merge(
                    task2_df[['review', 'date', 'sentiment_label', 'sentiment_score']],
                    on=merge_cols,
                    how='left',
                    suffixes=('', '_task2')
                )
                logger.info("Merged Task 2 sentiment data")
        
        # Transform each row
        for _, row in df.iterrows():
            bank_name = str(row['bank']).strip()
            bank_id = bank_mapping.get(bank_name)
            
            if bank_id is None:
                logger.warning(f"Unknown bank: {bank_name}, skipping review")
                continue
            
            # Prepare review data
            review_text = str(row['review']) if pd.notna(row['review']) else ''
            rating = int(row['rating']) if pd.notna(row['rating']) else None
            review_date = pd.to_datetime(row['date']).date() if pd.notna(row['date']) else None
            source = str(row.get('source', 'Google Play')) if pd.notna(row.get('source')) else 'Google Play'
            app_name = str(row.get('app_name', '')) if pd.notna(row.get('app_name')) else None
            
            # Handle collection_date
            collection_date = None
            if 'collection_date' in row and pd.notna(row['collection_date']):
                try:
                    collection_date = pd.to_datetime(row['collection_date']).date()
                except:
                    pass
            
            # Get sentiment data (from Task 2 merge or direct columns)
            sentiment_label = None
            sentiment_score = None
            
            if 'sentiment_label' in row and pd.notna(row['sentiment_label']):
                sentiment_label = str(row['sentiment_label']).lower()
                # Validate sentiment label
                if sentiment_label not in ['positive', 'negative', 'neutral']:
                    sentiment_label = None
            
            if 'sentiment_score' in row and pd.notna(row['sentiment_score']):
                try:
                    sentiment_score = float(row['sentiment_score'])
                except:
                    sentiment_score = None
            
            # Validate required fields
            if not review_text or rating is None or review_date is None:
                logger.warning(f"Skipping review with missing required fields")
                continue
            
            # Create record tuple
            record = (
                bank_id,
                review_text,
                rating,
                review_date,
                sentiment_label,
                sentiment_score,
                source,
                app_name,
                collection_date
            )
            
            records.append(record)
        
        logger.info(f"Transformed {len(records)} records for insertion")
        return records
    
    def insert_banks(self, banks_data: List[tuple]):
        """
        Insert bank data (usually already done by schema, but can be used for updates)
        
        Args:
            banks_data: List of (bank_name, app_name) tuples
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        insert_query = """
            INSERT INTO banks (bank_name, app_name)
            VALUES (%s, %s)
            ON CONFLICT (bank_name) DO UPDATE
            SET app_name = EXCLUDED.app_name,
                updated_at = CURRENT_TIMESTAMP
        """
        
        try:
            execute_batch(cursor, insert_query, banks_data)
            conn.commit()
            logger.info(f"[OK] Inserted/updated {len(banks_data)} banks")
        except psycopg2.Error as e:
            conn.rollback()
            logger.error(f"Failed to insert banks: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def insert_reviews(self, records: List[tuple]):
        """
        Insert review data in batches
        
        Args:
            records: List of review tuples
        """
        if not records:
            logger.warning("No records to insert")
            return
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        insert_query = """
            INSERT INTO reviews (
                bank_id, review_text, rating, review_date,
                sentiment_label, sentiment_score, source, app_name, collection_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """
        
        try:
            total_inserted = 0
            total_batches = (len(records) + self.batch_size - 1) // self.batch_size
            
            for i in range(0, len(records), self.batch_size):
                batch = records[i:i + self.batch_size]
                batch_num = (i // self.batch_size) + 1
                
                execute_batch(cursor, insert_query, batch)
                conn.commit()
                
                inserted = len(batch)
                total_inserted += inserted
                logger.info(f"  Batch {batch_num}/{total_batches}: Inserted {inserted} reviews")
            
            logger.info(f"[OK] Successfully inserted {total_inserted} reviews")
            
        except psycopg2.Error as e:
            conn.rollback()
            logger.error(f"Failed to insert reviews: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def validate_insertion(self) -> dict:
        """
        Validate that data was inserted correctly
        
        Returns:
            Dictionary with validation results
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        results = {}
        
        try:
            # Total reviews
            cursor.execute("SELECT COUNT(*) FROM reviews")
            results['total_reviews'] = cursor.fetchone()[0]
            
            # Reviews per bank
            cursor.execute("""
                SELECT b.bank_name, COUNT(r.review_id) AS count
                FROM banks b
                LEFT JOIN reviews r ON b.bank_id = r.bank_id
                GROUP BY b.bank_id, b.bank_name
                ORDER BY count DESC
            """)
            results['reviews_per_bank'] = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Average rating per bank
            cursor.execute("""
                SELECT b.bank_name, ROUND(AVG(r.rating), 2) AS avg_rating
                FROM banks b
                JOIN reviews r ON b.bank_id = r.bank_id
                GROUP BY b.bank_id, b.bank_name
                ORDER BY avg_rating DESC
            """)
            results['avg_rating_per_bank'] = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Reviews with sentiment
            cursor.execute("SELECT COUNT(*) FROM reviews WHERE sentiment_label IS NOT NULL")
            results['reviews_with_sentiment'] = cursor.fetchone()[0]
            
            # Null checks
            cursor.execute("SELECT COUNT(*) FROM reviews WHERE review_text IS NULL OR review_text = ''")
            results['null_review_text'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM reviews WHERE rating IS NULL")
            results['null_rating'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM reviews WHERE review_date IS NULL")
            results['null_review_date'] = cursor.fetchone()[0]
            
            # Foreign key integrity
            cursor.execute("""
                SELECT COUNT(*) 
                FROM reviews r
                LEFT JOIN banks b ON r.bank_id = b.bank_id
                WHERE b.bank_id IS NULL
            """)
            results['orphaned_reviews'] = cursor.fetchone()[0]
            
        except psycopg2.Error as e:
            logger.error(f"Validation query failed: {e}")
            results['error'] = str(e)
        finally:
            cursor.close()
            conn.close()
        
        return results
    
    def run_etl(self, input_file: Optional[str] = None, task2_file: Optional[str] = None):
        """
        Run complete ETL pipeline
        
        Args:
            input_file: Path to input CSV file (Task 1 processed data)
            task2_file: Path to Task 2 analyzed CSV file (optional)
        """
        logger.info("="*70)
        logger.info("Database ETL Pipeline")
        logger.info("Omega Consultancy - Task 3")
        logger.info("="*70)
        
        try:
            # Extract
            logger.info("\n[EXTRACT] Loading data...")
            df = self.load_data(input_file)
            task2_df = self.load_task2_data(task2_file)
            
            # Get bank mapping
            bank_mapping = self.get_bank_mapping()
            
            # Transform
            logger.info("\n[TRANSFORM] Transforming data...")
            records = self.transform_data(df, bank_mapping, task2_df)
            
            if not records:
                raise ValueError("No valid records to insert")
            
            # Load
            logger.info(f"\n[LOAD] Inserting {len(records)} reviews...")
            self.insert_reviews(records)
            
            # Validate
            logger.info("\n[VALIDATE] Validating insertion...")
            validation = self.validate_insertion()
            
            logger.info("\n" + "="*70)
            logger.info("ETL Pipeline Summary")
            logger.info("="*70)
            logger.info(f"Total reviews inserted: {validation['total_reviews']}")
            logger.info(f"\nReviews per bank:")
            for bank, count in validation['reviews_per_bank'].items():
                logger.info(f"  {bank}: {count}")
            logger.info(f"\nAverage rating per bank:")
            for bank, avg_rating in validation['avg_rating_per_bank'].items():
                logger.info(f"  {bank}: {avg_rating}")
            logger.info(f"\nReviews with sentiment: {validation['reviews_with_sentiment']}")
            logger.info(f"Data quality:")
            logger.info(f"  Null review_text: {validation['null_review_text']}")
            logger.info(f"  Null rating: {validation['null_rating']}")
            logger.info(f"  Null review_date: {validation['null_review_date']}")
            logger.info(f"  Orphaned reviews: {validation['orphaned_reviews']}")
            logger.info("="*70)
            logger.info("[OK] ETL pipeline completed successfully")
            logger.info("="*70)
            
            return validation
            
        except Exception as e:
            logger.error(f"[ERROR] ETL pipeline failed: {e}", exc_info=True)
            raise


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ETL pipeline for bank reviews')
    parser.add_argument('--input', type=str, default=None,
                       help='Path to input CSV file (Task 1 processed data)')
    parser.add_argument('--task2-input', type=str, default=None,
                       help='Path to Task 2 analyzed CSV file (optional)')
    parser.add_argument('--db-name', type=str, default='bank_reviews',
                       help='Database name')
    parser.add_argument('--host', type=str, default='localhost',
                       help='PostgreSQL host')
    parser.add_argument('--port', type=int, default=5432,
                       help='PostgreSQL port')
    parser.add_argument('--user', type=str, default='postgres',
                       help='PostgreSQL user')
    parser.add_argument('--password', type=str, default=None,
                       help='PostgreSQL password (or set POSTGRES_PASSWORD env var)')
    parser.add_argument('--batch-size', type=int, default=1000,
                       help='Batch size for inserts')
    
    args = parser.parse_args()
    
    # Run ETL
    etl = DatabaseETL(
        db_name=args.db_name,
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        batch_size=args.batch_size
    )
    etl.run_etl(input_file=args.input, task2_file=args.task2_input)


if __name__ == '__main__':
    main()

