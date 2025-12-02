"""
Task 2: Sentiment & Thematic Analysis Pipeline
Main execution script for sentiment analysis and thematic analysis
"""

import sys
import os
from datetime import datetime
import logging
import json
import pandas as pd
import uuid

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sentiment_analyzer import SentimentAnalyzer
from thematic_analyzer import ThematicAnalyzer
from nlp_pipeline import NLPipeline

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/task2_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Task2Pipeline:
    """Main pipeline for Task 2: Sentiment & Thematic Analysis"""
    
    def __init__(self, input_file: str = None, output_dir: str = 'data/analyzed'):
        """
        Initialize Task 2 pipeline
        
        Args:
            input_file: Path to processed CSV file (if None, uses most recent)
            output_dir: Directory to save output files
        """
        self.input_file = input_file
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize components
        logger.info("Initializing NLP components...")
        self.sentiment_analyzer = SentimentAnalyzer(compare_models=False)
        self.thematic_analyzer = ThematicAnalyzer(n_themes=5)
        self.nlp_pipeline = NLPipeline(use_spacy=True, use_nltk=True)
        logger.info("✓ All components initialized")
    
    def load_data(self) -> pd.DataFrame:
        """
        Load processed review data
        
        Returns:
            DataFrame with review data
        """
        if self.input_file is None:
            # Find most recent processed file
            processed_dir = 'data/processed'
            csv_files = [f for f in os.listdir(processed_dir) if f.endswith('.csv')]
            if not csv_files:
                raise FileNotFoundError(f"No CSV files found in {processed_dir}")
            self.input_file = os.path.join(processed_dir, sorted(csv_files)[-1])
            logger.info(f"Using most recent processed file: {self.input_file}")
        
        # Load CSV
        df = pd.read_csv(self.input_file)
        logger.info(f"Loaded {len(df)} reviews from {self.input_file}")
        
        # Check if review_id exists, if not generate it
        if 'review_id' not in df.columns:
            logger.info("review_id not found. Generating unique IDs...")
            df['review_id'] = [str(uuid.uuid4()) for _ in range(len(df))]
        
        # Ensure we have required columns
        required_columns = ['review', 'rating', 'bank']
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        
        return df
    
    def add_review_id_from_raw(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Try to add review_id from raw JSON file if available
        
        Args:
            df: DataFrame without review_id
            
        Returns:
            DataFrame with review_id if found
        """
        # Try to load from raw JSON
        raw_dir = 'data/raw'
        json_files = [f for f in os.listdir(raw_dir) if f.endswith('.json')]
        
        if json_files:
            # Use most recent raw file
            raw_file = os.path.join(raw_dir, sorted(json_files)[-1])
            logger.info(f"Attempting to load review_id from: {raw_file}")
            
            try:
                with open(raw_file, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                
                # Create mapping from review text + date to review_id
                id_mapping = {}
                for bank, reviews in raw_data.items():
                    for review in reviews:
                        key = (review.get('review', ''), review.get('date', ''))
                        if key[0] and key[1]:
                            id_mapping[key] = review.get('review_id', None)
                
                # Map IDs to dataframe
                df['review_id'] = df.apply(
                    lambda row: id_mapping.get((row['review'], row['date']), None),
                    axis=1
                )
                
                # Generate IDs for unmatched reviews
                missing_count = df['review_id'].isna().sum()
                if missing_count > 0:
                    logger.info(f"Generating IDs for {missing_count} unmatched reviews")
                    df.loc[df['review_id'].isna(), 'review_id'] = [
                        str(uuid.uuid4()) for _ in range(missing_count)
                    ]
                
                logger.info(f"✓ Loaded review_id for {len(df) - missing_count} reviews")
                
            except Exception as e:
                logger.warning(f"Could not load review_id from raw file: {e}")
                df['review_id'] = [str(uuid.uuid4()) for _ in range(len(df))]
        else:
            df['review_id'] = [str(uuid.uuid4()) for _ in range(len(df))]
        
        return df
    
    def run_sentiment_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Run sentiment analysis on reviews
        
        Args:
            df: DataFrame with reviews
            
        Returns:
            DataFrame with sentiment analysis results
        """
        logger.info("\n" + "="*70)
        logger.info("STEP 1: Sentiment Analysis")
        logger.info("="*70)
        
        # Analyze sentiment
        df_with_sentiment = self.sentiment_analyzer.analyze_dataframe(
            df, 
            text_column='review',
            batch_size=32
        )
        
        # Aggregate insights
        insights = self.sentiment_analyzer.aggregate_sentiment_insights(df_with_sentiment)
        
        # Log insights
        logger.info("\nSentiment Insights:")
        logger.info(f"  Overall distribution: {insights.get('overall', {})}")
        logger.info(f"  Average sentiment score: {insights.get('avg_sentiment_score', 0):.4f}")
        
        if 'by_bank' in insights:
            logger.info("\n  By Bank:")
            for bank, data in insights['by_bank'].items():
                logger.info(f"    {bank}: {data['avg_score']:.4f} (n={data['count']})")
        
        if 'by_rating' in insights:
            logger.info("\n  By Rating:")
            for rating, data in insights['by_rating'].items():
                logger.info(f"    {rating} stars: {data['avg_score']:.4f} (n={data['count']})")
        
        # Calculate success rate
        success_rate = (df_with_sentiment['sentiment_label'].notna().sum() / len(df_with_sentiment)) * 100
        logger.info(f"\n✓ Sentiment analysis completed: {success_rate:.1f}% success rate")
        
        return df_with_sentiment
    
    def run_thematic_analysis(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Run thematic analysis on reviews
        
        Args:
            df: DataFrame with reviews
            
        Returns:
            Tuple of (DataFrame with themes, theme dictionary)
        """
        logger.info("\n" + "="*70)
        logger.info("STEP 2: Thematic Analysis")
        logger.info("="*70)
        
        # Analyze themes
        df_with_themes, all_themes = self.thematic_analyzer.analyze_dataframe(
            df,
            text_column='review',
            bank_column='bank'
        )
        
        # Log theme insights
        logger.info("\nThemes Identified:")
        for bank, themes in all_themes.items():
            logger.info(f"\n  {bank} ({len(themes)} themes):")
            for theme_name, theme_data in themes.items():
                keywords = theme_data.get('keywords', [])[:5]  # Top 5 keywords
                count = theme_data.get('review_count', 0)
                logger.info(f"    - {theme_name}: {count} reviews")
                logger.info(f"      Keywords: {', '.join(keywords)}")
        
        logger.info("\n✓ Thematic analysis completed")
        
        return df_with_themes, all_themes
    
    def run_nlp_processing(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Run NLP text processing pipeline
        
        Args:
            df: DataFrame with reviews
            
        Returns:
            DataFrame with processed text
        """
        logger.info("\n" + "="*70)
        logger.info("STEP 3: NLP Text Processing")
        logger.info("="*70)
        
        # Process texts
        df_processed = self.nlp_pipeline.process_dataframe(
            df,
            text_column='review',
            processed_column='processed_text',
            normalize=True,
            tokenize=True,
            remove_stopwords=True,
            lemmatize=True,
            return_string=True
        )
        
        logger.info("✓ NLP processing completed")
        
        return df_processed
    
    def create_output_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create final output DataFrame with required fields
        
        Args:
            df: DataFrame with all analysis results
            
        Returns:
            DataFrame with required output columns
        """
        # Select and rename columns
        output_columns = {
            'review_id': 'review_id',
            'review': 'review_text',
            'sentiment_label': 'sentiment_label',
            'sentiment_score': 'sentiment_score',
            'identified_themes': 'identified_themes',
            'primary_theme': 'primary_theme',
            'bank': 'bank',
            'rating': 'rating',
            'date': 'date'
        }
        
        # Create output dataframe
        output_df = pd.DataFrame()
        for output_col, input_col in output_columns.items():
            if input_col in df.columns:
                output_df[output_col] = df[input_col]
            else:
                logger.warning(f"Column '{input_col}' not found, skipping '{output_col}'")
        
        # Ensure required columns exist
        required = ['review_id', 'review_text', 'sentiment_label', 'sentiment_score', 'identified_themes']
        missing = [col for col in required if col not in output_df.columns]
        if missing:
            raise ValueError(f"Missing required output columns: {missing}")
        
        # Fill missing values
        output_df['identified_themes'] = output_df['identified_themes'].fillna('Uncategorized')
        output_df['primary_theme'] = output_df['primary_theme'].fillna('Uncategorized')
        
        return output_df
    
    def save_results(self, df: pd.DataFrame, all_themes: Dict, insights: Dict):
        """
        Save analysis results to CSV and JSON
        
        Args:
            df: Final output DataFrame
            all_themes: Dictionary of themes by bank
            insights: Sentiment insights dictionary
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save main results CSV
        csv_filename = f'sentiment_thematic_analysis_{timestamp}.csv'
        csv_path = os.path.join(self.output_dir, csv_filename)
        df.to_csv(csv_path, index=False, encoding='utf-8')
        logger.info(f"\n✓ Results saved to: {csv_path}")
        
        # Save themes JSON
        themes_filename = f'themes_{timestamp}.json'
        themes_path = os.path.join(self.output_dir, themes_filename)
        with open(themes_path, 'w', encoding='utf-8') as f:
            json.dump(all_themes, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ Themes saved to: {themes_path}")
        
        # Save insights JSON
        insights_filename = f'sentiment_insights_{timestamp}.json'
        insights_path = os.path.join(self.output_dir, insights_filename)
        with open(insights_path, 'w', encoding='utf-8') as f:
            json.dump(insights, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"✓ Insights saved to: {insights_path}")
        
        return csv_path, themes_path, insights_path
    
    def validate_kpis(self, df: pd.DataFrame) -> Dict[str, bool]:
        """
        Validate that KPIs are met
        
        Args:
            df: Output DataFrame
            
        Returns:
            Dictionary of KPI validation results
        """
        logger.info("\n" + "="*70)
        logger.info("KPI Validation")
        logger.info("="*70)
        
        kpis = {}
        
        # Sentiment scores computed for ≥ 90% of reviews
        sentiment_success = df['sentiment_label'].notna().sum()
        sentiment_rate = (sentiment_success / len(df)) * 100
        kpis['sentiment_90pct'] = sentiment_rate >= 90
        logger.info(f"  Sentiment scores ≥90%: {'✓' if kpis['sentiment_90pct'] else '✗'} "
                   f"({sentiment_rate:.1f}%)")
        
        # ≥ 3 themes per bank
        themes_per_bank = {}
        if 'bank' in df.columns and 'primary_theme' in df.columns:
            for bank in df['bank'].unique():
                bank_df = df[df['bank'] == bank]
                unique_themes = bank_df['primary_theme'].nunique()
                themes_per_bank[bank] = unique_themes
                kpi_met = unique_themes >= 3
                logger.info(f"  {bank} themes ≥3: {'✓' if kpi_met else '✗'} ({unique_themes} themes)")
        
        kpis['themes_per_bank'] = all(count >= 3 for count in themes_per_bank.values()) if themes_per_bank else False
        
        # Minimum 400 reviews analyzed
        kpis['min_reviews'] = len(df) >= 400
        logger.info(f"  Reviews analyzed ≥400: {'✓' if kpis['min_reviews'] else '✗'} ({len(df)})")
        
        # Minimum 2 themes per bank (minimum essential)
        kpis['min_themes_per_bank'] = all(count >= 2 for count in themes_per_bank.values()) if themes_per_bank else False
        
        all_met = all(kpis.values())
        logger.info(f"\n  Overall: {'✓ All KPIs met!' if all_met else '✗ Some KPIs not met'}")
        
        return kpis
    
    def run(self):
        """
        Run complete Task 2 pipeline
        """
        logger.info("="*70)
        logger.info("Task 2: Sentiment & Thematic Analysis Pipeline")
        logger.info("Omega Consultancy")
        logger.info("="*70)
        
        try:
            # Load data
            df = self.load_data()
            
            # Add review_id if missing
            if 'review_id' not in df.columns or df['review_id'].isna().any():
                df = self.add_review_id_from_raw(df)
            
            initial_count = len(df)
            logger.info(f"\nStarting analysis for {initial_count} reviews")
            
            # Step 1: Sentiment Analysis
            df = self.run_sentiment_analysis(df)
            
            # Step 2: Thematic Analysis
            df, all_themes = self.run_thematic_analysis(df)
            
            # Step 3: NLP Processing (optional, for downstream use)
            df = self.run_nlp_processing(df)
            
            # Create output DataFrame
            output_df = self.create_output_dataframe(df)
            
            # Get sentiment insights for saving
            insights = self.sentiment_analyzer.aggregate_sentiment_insights(df)
            
            # Save results
            csv_path, themes_path, insights_path = self.save_results(output_df, all_themes, insights)
            
            # Validate KPIs
            kpis = self.validate_kpis(output_df)
            
            # Final summary
            logger.info("\n" + "="*70)
            logger.info("PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("="*70)
            logger.info(f"Total reviews analyzed: {len(output_df)}")
            logger.info(f"Output CSV: {csv_path}")
            logger.info(f"Themes JSON: {themes_path}")
            logger.info(f"Insights JSON: {insights_path}")
            logger.info("="*70)
            
            return output_df, all_themes, insights
            
        except Exception as e:
            logger.error(f"\n✗ Pipeline failed with error: {str(e)}", exc_info=True)
            raise


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Task 2: Sentiment & Thematic Analysis')
    parser.add_argument('--input', type=str, default=None,
                       help='Path to input CSV file (default: most recent processed file)')
    parser.add_argument('--output-dir', type=str, default='data/analyzed',
                       help='Output directory for results')
    
    args = parser.parse_args()
    
    # Run pipeline
    pipeline = Task2Pipeline(input_file=args.input, output_dir=args.output_dir)
    pipeline.run()


if __name__ == '__main__':
    main()

