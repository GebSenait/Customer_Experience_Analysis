"""
Task 3: PostgreSQL Database Setup & ETL Pipeline
Main execution script for database setup and data ingestion
Omega Consultancy
"""

import sys
import os
from datetime import datetime
import logging
import argparse

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_setup import DatabaseSetup
from database_etl import DatabaseETL

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/task3_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Task3Pipeline:
    """Main pipeline for Task 3: Database Setup & ETL"""
    
    def __init__(
        self,
        db_name: str = 'bank_reviews',
        host: str = 'localhost',
        port: int = 5432,
        user: str = 'postgres',
        password: str = None,
        schema_file: str = 'database/schema.sql',
        input_file: str = None,
        task2_file: str = None,
        skip_setup: bool = False
    ):
        """
        Initialize Task 3 pipeline
        
        Args:
            db_name: Database name
            host: PostgreSQL host
            port: PostgreSQL port
            user: PostgreSQL user
            password: PostgreSQL password
            schema_file: Path to schema SQL file
            input_file: Path to input CSV file
            task2_file: Path to Task 2 analyzed CSV file
            skip_setup: Skip database setup if True
        """
        self.db_name = db_name
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.schema_file = schema_file
        self.input_file = input_file
        self.task2_file = task2_file
        self.skip_setup = skip_setup
        
        # Initialize components
        self.db_setup = DatabaseSetup(
            db_name=db_name,
            host=host,
            port=port,
            user=user,
            password=password
        )
        
        self.etl = DatabaseETL(
            db_name=db_name,
            host=host,
            port=port,
            user=user,
            password=password
        )
    
    def run_setup(self):
        """Run database setup"""
        logger.info("\n" + "="*70)
        logger.info("STEP 1: Database Setup")
        logger.info("="*70)
        
        self.db_setup.setup(schema_file=self.schema_file)
    
    def run_etl(self):
        """Run ETL pipeline"""
        logger.info("\n" + "="*70)
        logger.info("STEP 2: Data ETL")
        logger.info("="*70)
        
        validation = self.etl.run_etl(
            input_file=self.input_file,
            task2_file=self.task2_file
        )
        
        return validation
    
    def validate_kpis(self, validation: dict) -> dict:
        """
        Validate Task 3 KPIs
        
        Args:
            validation: Validation results from ETL
            
        Returns:
            Dictionary of KPI validation results
        """
        logger.info("\n" + "="*70)
        logger.info("KPI Validation")
        logger.info("="*70)
        
        kpis = {}
        
        # Fully working PostgreSQL connection & ETL insert script
        kpis['connection_working'] = 'error' not in validation
        logger.info(f"  PostgreSQL connection working: {'✓' if kpis['connection_working'] else '✗'}")
        
        # Database populated with ≥ 1,000 review rows
        total_reviews = validation.get('total_reviews', 0)
        kpis['min_1000_reviews'] = total_reviews >= 1000
        logger.info(f"  Reviews ≥1,000: {'✓' if kpis['min_1000_reviews'] else '✗'} ({total_reviews})")
        
        # Minimum essential: ≥ 400 reviews
        kpis['min_400_reviews'] = total_reviews >= 400
        logger.info(f"  Reviews ≥400 (minimum): {'✓' if kpis['min_400_reviews'] else '✗'} ({total_reviews})")
        
        # Data integrity checks
        kpis['no_orphaned_reviews'] = validation.get('orphaned_reviews', 0) == 0
        logger.info(f"  No orphaned reviews: {'✓' if kpis['no_orphaned_reviews'] else '✗'} "
                   f"({validation.get('orphaned_reviews', 0)} orphaned)")
        
        kpis['no_null_critical_fields'] = (
            validation.get('null_review_text', 0) == 0 and
            validation.get('null_rating', 0) == 0 and
            validation.get('null_review_date', 0) == 0
        )
        logger.info(f"  No nulls in critical fields: {'✓' if kpis['no_null_critical_fields'] else '✗'}")
        
        # Schema committed (checked separately)
        schema_exists = os.path.exists(self.schema_file)
        kpis['schema_committed'] = schema_exists
        logger.info(f"  Schema file exists: {'✓' if kpis['schema_committed'] else '✗'}")
        
        all_met = all(kpis.values())
        logger.info(f"\n  Overall: {'✓ All KPIs met!' if all_met else '✗ Some KPIs not met'}")
        
        return kpis
    
    def run(self):
        """Run complete Task 3 pipeline"""
        logger.info("="*70)
        logger.info("Task 3: PostgreSQL Database Setup & ETL Pipeline")
        logger.info("Omega Consultancy")
        logger.info("="*70)
        
        try:
            # Step 1: Database Setup
            if not self.skip_setup:
                self.run_setup()
            else:
                logger.info("Skipping database setup (--skip-setup flag)")
            
            # Step 2: ETL
            validation = self.run_etl()
            
            # Step 3: KPI Validation
            kpis = self.validate_kpis(validation)
            
            # Final summary
            logger.info("\n" + "="*70)
            logger.info("PIPELINE COMPLETED")
            logger.info("="*70)
            logger.info(f"Total reviews in database: {validation.get('total_reviews', 0)}")
            logger.info(f"Database: {self.db_name}")
            logger.info(f"Host: {self.host}:{self.port}")
            logger.info("="*70)
            
            return validation, kpis
            
        except Exception as e:
            error_msg = str(e)
            if "no password supplied" in error_msg.lower() or "fe_sendauth" in error_msg.lower():
                logger.error("\n[ERROR] Pipeline failed: PostgreSQL password not provided")
                logger.error("")
                logger.error("SOLUTION:")
                logger.error("  1. Set the password environment variable:")
                logger.error("     PowerShell: $env:POSTGRES_PASSWORD='your_password'")
                logger.error("     CMD:        set POSTGRES_PASSWORD=your_password")
                logger.error("")
                logger.error("  2. Or pass password as argument:")
                logger.error("     python src/task3_main.py --password your_password")
                logger.error("")
                logger.error("  3. Then run the pipeline again:")
                logger.error("     python src/task3_main.py")
            else:
                logger.error(f"\n[ERROR] Pipeline failed with error: {error_msg}", exc_info=True)
            raise


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='Task 3: PostgreSQL Database Setup & ETL Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full pipeline (setup + ETL)
  python src/task3_main.py
  
  # Skip setup (database already exists)
  python src/task3_main.py --skip-setup
  
  # Custom database connection
  python src/task3_main.py --host localhost --port 5432 --user postgres
  
  # Specify input files
  python src/task3_main.py --input data/processed/reviews_cleaned_20251202_092120.csv --task2-input data/analyzed/sentiment_thematic_analysis_*.csv
        """
    )
    
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
    parser.add_argument('--input', type=str, default=None,
                       help='Path to input CSV file (Task 1 processed data)')
    parser.add_argument('--task2-input', type=str, default=None,
                       help='Path to Task 2 analyzed CSV file (optional)')
    parser.add_argument('--skip-setup', action='store_true',
                       help='Skip database setup (use if database already exists)')
    
    args = parser.parse_args()
    
    # Run pipeline
    pipeline = Task3Pipeline(
        db_name=args.db_name,
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        schema_file=args.schema_file,
        input_file=args.input,
        task2_file=args.task2_input,
        skip_setup=args.skip_setup
    )
    pipeline.run()


if __name__ == '__main__':
    main()

