"""
Data Preprocessing Module
Cleans and standardizes review data for analysis
"""

import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/preprocessor_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Preprocesses and cleans review data"""
    
    def __init__(self, input_dir: str = 'data/raw', output_dir: str = 'data/processed'):
        """
        Initialize preprocessor
        
        Args:
            input_dir: Directory containing raw JSON files
            output_dir: Directory to save processed CSV files
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs('logs', exist_ok=True)
    
    def load_raw_data(self, filepath: Optional[str] = None) -> pd.DataFrame:
        """
        Load raw JSON data into DataFrame
        
        Args:
            filepath: Path to JSON file. If None, loads most recent file
            
        Returns:
            DataFrame with raw review data
        """
        if filepath is None:
            # Find most recent raw data file
            json_files = [f for f in os.listdir(self.input_dir) if f.endswith('.json')]
            if not json_files:
                raise FileNotFoundError(f"No JSON files found in {self.input_dir}")
            filepath = os.path.join(self.input_dir, sorted(json_files)[-1])
            logger.info(f"Loading most recent file: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Flatten nested structure
        records = []
        for bank, reviews in data.items():
            for review in reviews:
                records.append(review)
        
        df = pd.DataFrame(records)
        logger.info(f"Loaded {len(df)} reviews from {len(data)} banks")
        
        return df
    
    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate reviews
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with duplicates removed
        """
        initial_count = len(df)
        
        # Remove duplicates based on review text and date
        df = df.drop_duplicates(subset=['review', 'date'], keep='first')
        
        removed = initial_count - len(df)
        logger.info(f"Removed {removed} duplicate reviews ({initial_count} -> {len(df)})")
        
        return df
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values in the dataset
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with missing values handled
        """
        initial_count = len(df)
        
        # Drop rows with missing review text (critical field)
        df = df.dropna(subset=['review'])
        logger.info(f"Removed {initial_count - len(df)} rows with missing review text")
        
        # Fill missing ratings with median
        if 'rating' in df.columns:
            median_rating = df['rating'].median()
            missing_ratings = df['rating'].isna().sum()
            df['rating'] = df['rating'].fillna(median_rating)
            if missing_ratings > 0:
                logger.info(f"Filled {missing_ratings} missing ratings with median: {median_rating}")
        
        # Remove rows with missing dates
        initial_count = len(df)
        df = df.dropna(subset=['date'])
        logger.info(f"Removed {initial_count - len(df)} rows with missing dates")
        
        return df
    
    def normalize_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize dates to YYYY-MM-DD format
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with normalized dates
        """
        if 'date' not in df.columns:
            logger.warning("No 'date' column found")
            return df
        
        # Convert to datetime and format
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Remove rows where date conversion failed
        invalid_dates = df['date'].isna().sum()
        if invalid_dates > 0:
            logger.warning(f"Removed {invalid_dates} rows with invalid dates")
            df = df.dropna(subset=['date'])
        
        # Format to YYYY-MM-DD
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')
        
        logger.info("Dates normalized to YYYY-MM-DD format")
        return df
    
    def normalize_text(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize review text
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with normalized text
        """
        if 'review' not in df.columns:
            return df
        
        # Remove extra whitespace
        df['review'] = df['review'].str.strip()
        df['review'] = df['review'].str.replace(r'\s+', ' ', regex=True)
        
        # Remove empty reviews
        initial_count = len(df)
        df = df[df['review'].str.len() > 0]
        logger.info(f"Removed {initial_count - len(df)} empty reviews after normalization")
        
        return df
    
    def validate_ratings(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and clean ratings
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with validated ratings
        """
        if 'rating' not in df.columns:
            return df
        
        # Ensure ratings are between 1-5
        initial_count = len(df)
        df = df[(df['rating'] >= 1) & (df['rating'] <= 5)]
        
        # Convert to integer
        df['rating'] = df['rating'].astype(int)
        
        removed = initial_count - len(df)
        if removed > 0:
            logger.warning(f"Removed {removed} rows with invalid ratings")
        
        logger.info("Ratings validated (1-5 range)")
        return df
    
    def add_metadata(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add consistent metadata fields
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with metadata added
        """
        # Ensure source field exists
        if 'source' not in df.columns:
            df['source'] = 'Google Play'
        
        # Add collection date
        df['collection_date'] = datetime.now().strftime('%Y-%m-%d')
        
        # Ensure bank field exists
        if 'bank' not in df.columns:
            logger.warning("No 'bank' column found. Attempting to infer from app_name...")
            # Try to infer from app_name if possible
            df['bank'] = df.get('app_name', 'Unknown')
        
        logger.info("Metadata fields added")
        return df
    
    def select_final_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Select and order final columns for output
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with selected columns
        """
        required_columns = ['review', 'rating', 'date', 'bank', 'source']
        optional_columns = ['app_name', 'collection_date']
        
        # Ensure required columns exist
        missing_required = [col for col in required_columns if col not in df.columns]
        if missing_required:
            raise ValueError(f"Missing required columns: {missing_required}")
        
        # Select columns
        final_columns = required_columns + [col for col in optional_columns if col in df.columns]
        df = df[final_columns]
        
        return df
    
    def calculate_quality_metrics(self, df: pd.DataFrame) -> Dict:
        """
        Calculate data quality metrics
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary of quality metrics
        """
        total_rows = len(df)
        total_cells = total_rows * len(df.columns)
        missing_cells = df.isna().sum().sum()
        missing_pct = (missing_cells / total_cells * 100) if total_cells > 0 else 0
        
        metrics = {
            'total_reviews': total_rows,
            'reviews_per_bank': df['bank'].value_counts().to_dict() if 'bank' in df.columns else {},
            'missing_cells': missing_cells,
            'missing_percentage': round(missing_pct, 2),
            'columns': list(df.columns),
            'date_range': {
                'min': df['date'].min() if 'date' in df.columns else None,
                'max': df['date'].max() if 'date' in df.columns else None
            } if 'date' in df.columns else {}
        }
        
        return metrics
    
    def preprocess(self, input_file: Optional[str] = None) -> pd.DataFrame:
        """
        Run complete preprocessing pipeline
        
        Args:
            input_file: Path to input JSON file (optional)
            
        Returns:
            Cleaned DataFrame
        """
        logger.info("="*60)
        logger.info("Starting Data Preprocessing")
        logger.info("="*60)
        
        # Load data
        df = self.load_raw_data(input_file)
        initial_count = len(df)
        logger.info(f"Initial review count: {initial_count}")
        
        # Remove duplicates
        df = self.remove_duplicates(df)
        
        # Handle missing values
        df = self.handle_missing_values(df)
        
        # Normalize dates
        df = self.normalize_dates(df)
        
        # Normalize text
        df = self.normalize_text(df)
        
        # Validate ratings
        df = self.validate_ratings(df)
        
        # Add metadata
        df = self.add_metadata(df)
        
        # Select final columns
        df = self.select_final_columns(df)
        
        # Calculate metrics
        metrics = self.calculate_quality_metrics(df)
        
        logger.info("\n" + "="*60)
        logger.info("Preprocessing Summary")
        logger.info("="*60)
        logger.info(f"Initial reviews: {initial_count}")
        logger.info(f"Final reviews: {len(df)}")
        logger.info(f"Removed: {initial_count - len(df)} ({((initial_count - len(df))/initial_count*100):.1f}%)")
        logger.info(f"Missing data: {metrics['missing_percentage']}%")
        logger.info(f"\nReviews per bank:")
        for bank, count in metrics['reviews_per_bank'].items():
            logger.info(f"  {bank}: {count}")
        logger.info("="*60)
        
        # Validate KPIs
        self.validate_kpis(df, metrics)
        
        return df
    
    def validate_kpis(self, df: pd.DataFrame, metrics: Dict):
        """
        Validate that KPIs are met
        
        Args:
            df: Processed DataFrame
            metrics: Quality metrics dictionary
        """
        logger.info("\nKPI Validation:")
        
        # Total reviews >= 1200
        total = len(df)
        kpi_total = total >= 1200
        logger.info(f"  Total reviews ≥1,200: {'✓' if kpi_total else '✗'} ({total})")
        
        # Missing data <5%
        kpi_missing = metrics['missing_percentage'] < 5
        logger.info(f"  Missing data <5%: {'✓' if kpi_missing else '✗'} ({metrics['missing_percentage']}%)")
        
        # Per bank >= 400
        kpi_per_bank = all(count >= 400 for count in metrics['reviews_per_bank'].values())
        logger.info(f"  Per bank ≥400: {'✓' if kpi_per_bank else '✗'}")
        for bank, count in metrics['reviews_per_bank'].items():
            status = '✓' if count >= 400 else '✗'
            logger.info(f"    {bank}: {status} ({count})")
        
        if kpi_total and kpi_missing and kpi_per_bank:
            logger.info("\n✓ All KPIs met!")
        else:
            logger.warning("\n✗ Some KPIs not met. Review data collection.")
    
    def save_processed_data(self, df: pd.DataFrame, filename: Optional[str] = None):
        """
        Save processed data to CSV
        
        Args:
            df: Processed DataFrame
            filename: Optional custom filename
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'reviews_cleaned_{timestamp}.csv'
        
        filepath = os.path.join(self.output_dir, filename)
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        logger.info(f"\nProcessed data saved to: {filepath}")
        return filepath


def main():
    """Main execution function"""
    preprocessor = DataPreprocessor()
    
    # Run preprocessing
    df = preprocessor.preprocess()
    
    # Save processed data
    if len(df) > 0:
        preprocessor.save_processed_data(df)
        logger.info("\n✓ Preprocessing completed successfully!")
    else:
        logger.error("\n✗ No data to save. Check input files.")
    
    return df


if __name__ == '__main__':
    main()

