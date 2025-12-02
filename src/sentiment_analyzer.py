"""
Sentiment Analysis Module
Implements robust sentiment scoring using distilbert-base-uncased-finetuned-sst-2-english
with optional comparison to VADER and TextBlob
"""

import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

# Import torch with error handling
TORCH_AVAILABLE = False
torch = None
torch_error = None
try:
    import torch
    TORCH_AVAILABLE = True
except Exception as e:
    torch_error = str(e)

# Import transformers (depends on torch)
TRANSFORMERS_AVAILABLE = False
AutoTokenizer = None
AutoModelForSequenceClassification = None
transformers_error = None
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    TRANSFORMERS_AVAILABLE = TORCH_AVAILABLE
except Exception as e:
    transformers_error = str(e)

# Import other sentiment analyzers
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    SentimentIntensityAnalyzer = None

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    TextBlob = None

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Sentiment analysis using multiple models"""
    
    def __init__(self, model_name: str = "distilbert-base-uncased-finetuned-sst-2-english", 
                 use_gpu: bool = False, compare_models: bool = False):
        """
        Initialize sentiment analyzer
        
        Args:
            model_name: HuggingFace model name for sentiment analysis
            use_gpu: Whether to use GPU if available
            compare_models: Whether to also run VADER and TextBlob for comparison
        """
        # Check dependencies
        if not TORCH_AVAILABLE:
            error_msg = f"PyTorch is not available. Error: {torch_error or 'Unknown error'}"
            logger.error(error_msg)
            raise ImportError(
                error_msg + "\n"
                "Please fix torch installation:\n"
                "1. Run: fix_torch_issue.bat\n"
                "2. Or: pip uninstall torch && pip install torch --index-url https://download.pytorch.org/whl/cpu\n"
                "3. Install Visual C++ Redistributables if needed"
            )
        
        if not TRANSFORMERS_AVAILABLE:
            error_msg = f"Transformers library is not available. Error: {transformers_error or 'Unknown error'}"
            logger.error(error_msg)
            raise ImportError(error_msg + "\nPlease install: pip install transformers")
        
        self.model_name = model_name
        self.device = torch.device("cuda" if use_gpu and torch.cuda.is_available() else "cpu")
        self.compare_models = compare_models
        
        logger.info(f"Initializing sentiment analyzer with model: {model_name}")
        logger.info(f"Using device: {self.device}")
        
        # Load distilbert model
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            logger.info("✓ DistilBERT model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
        
        # Initialize comparison models if requested
        if compare_models:
            if VADER_AVAILABLE:
                self.vader_analyzer = SentimentIntensityAnalyzer()
                logger.info("✓ VADER analyzer initialized")
            else:
                logger.warning("VADER not available, skipping comparison")
                self.vader_analyzer = None
            
            if TEXTBLOB_AVAILABLE:
                logger.info("✓ TextBlob ready for use")
            else:
                logger.warning("TextBlob not available, skipping comparison")
    
    def predict_sentiment_distilbert(self, text: str) -> Tuple[str, float]:
        """
        Predict sentiment using DistilBERT model
        
        Args:
            text: Input text to analyze
            
        Returns:
            Tuple of (label, score) where label is 'positive' or 'negative' and score is confidence
        """
        if not text or pd.isna(text):
            return 'neutral', 0.5
        
        try:
            # Tokenize and encode
            inputs = self.tokenizer(
                text,
                truncation=True,
                padding=True,
                max_length=512,
                return_tensors="pt"
            ).to(self.device)
            
            # Predict
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=-1)
            
            # Get predictions
            predicted_class = torch.argmax(probabilities, dim=-1).item()
            confidence = probabilities[0][predicted_class].item()
            
            # Map to labels (model outputs: 0=negative, 1=positive)
            label = "positive" if predicted_class == 1 else "negative"
            
            return label, confidence
            
        except Exception as e:
            logger.warning(f"Error in distilbert prediction for text: {text[:50]}... Error: {e}")
            return 'neutral', 0.5
    
    def predict_sentiment_vader(self, text: str) -> Tuple[str, float]:
        """
        Predict sentiment using VADER
        
        Args:
            text: Input text to analyze
            
        Returns:
            Tuple of (label, score) where score is compound score from -1 to 1
        """
        if not text or pd.isna(text):
            return 'neutral', 0.0
        
        if not VADER_AVAILABLE or self.vader_analyzer is None:
            return 'neutral', 0.5
        
        try:
            scores = self.vader_analyzer.polarity_scores(text)
            compound = scores['compound']
            
            # Classify based on compound score
            if compound >= 0.05:
                label = 'positive'
            elif compound <= -0.05:
                label = 'negative'
            else:
                label = 'neutral'
            
            # Normalize score to 0-1 range for consistency
            normalized_score = (compound + 1) / 2
            
            return label, normalized_score
            
        except Exception as e:
            logger.warning(f"Error in VADER prediction: {e}")
            return 'neutral', 0.5
    
    def predict_sentiment_textblob(self, text: str) -> Tuple[str, float]:
        """
        Predict sentiment using TextBlob
        
        Args:
            text: Input text to analyze
            
        Returns:
            Tuple of (label, score) where score is polarity from -1 to 1
        """
        if not text or pd.isna(text):
            return 'neutral', 0.0
        
        if not TEXTBLOB_AVAILABLE:
            return 'neutral', 0.5
        
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            # Classify based on polarity
            if polarity > 0.1:
                label = 'positive'
            elif polarity < -0.1:
                label = 'negative'
            else:
                label = 'neutral'
            
            # Normalize score to 0-1 range
            normalized_score = (polarity + 1) / 2
            
            return label, normalized_score
            
        except Exception as e:
            logger.warning(f"Error in TextBlob prediction: {e}")
            return 'neutral', 0.5
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment using primary model and optionally compare with others
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        # Primary analysis with DistilBERT
        label, score = self.predict_sentiment_distilbert(text)
        
        result = {
            'sentiment_label': label,
            'sentiment_score': round(score, 4)
        }
        
        # Add comparison results if requested
        if self.compare_models:
            vader_label, vader_score = self.predict_sentiment_vader(text)
            textblob_label, textblob_score = self.predict_sentiment_textblob(text)
            
            result.update({
                'vader_label': vader_label,
                'vader_score': round(vader_score, 4),
                'textblob_label': textblob_label,
                'textblob_score': round(textblob_score, 4)
            })
        
        return result
    
    def analyze_batch(self, texts: List[str], batch_size: int = 32, 
                     show_progress: bool = True) -> List[Dict]:
        """
        Analyze sentiment for a batch of texts
        
        Args:
            texts: List of texts to analyze
            batch_size: Batch size for processing
            show_progress: Whether to show progress bar
            
        Returns:
            List of sentiment analysis results
        """
        results = []
        
        if show_progress:
            from tqdm import tqdm
            iterator = tqdm(texts, desc="Analyzing sentiment")
        else:
            iterator = texts
        
        for text in iterator:
            result = self.analyze_sentiment(text)
            results.append(result)
        
        return results
    
    def analyze_dataframe(self, df: pd.DataFrame, text_column: str = 'review',
                         batch_size: int = 32) -> pd.DataFrame:
        """
        Analyze sentiment for all reviews in a DataFrame
        
        Args:
            df: DataFrame with review texts
            text_column: Name of column containing review text
            batch_size: Batch size for processing
            
        Returns:
            DataFrame with sentiment columns added
        """
        logger.info(f"Analyzing sentiment for {len(df)} reviews...")
        
        # Analyze all texts
        texts = df[text_column].tolist()
        results = self.analyze_batch(texts, batch_size=batch_size)
        
        # Convert results to DataFrame
        results_df = pd.DataFrame(results)
        
        # Merge with original DataFrame
        output_df = df.copy()
        for col in results_df.columns:
            output_df[col] = results_df[col].values
        
        # Calculate success rate
        successful = output_df['sentiment_label'].notna().sum()
        success_rate = (successful / len(output_df)) * 100
        logger.info(f"Sentiment analysis completed: {successful}/{len(output_df)} reviews ({success_rate:.1f}%)")
        
        return output_df
    
    def aggregate_sentiment_insights(self, df: pd.DataFrame) -> Dict:
        """
        Aggregate sentiment insights by bank, rating, and category
        
        Args:
            df: DataFrame with sentiment analysis results
            
        Returns:
            Dictionary with aggregated insights
        """
        insights = {}
        
        # Overall sentiment distribution
        if 'sentiment_label' in df.columns:
            insights['overall'] = df['sentiment_label'].value_counts().to_dict()
            insights['overall_pct'] = (df['sentiment_label'].value_counts(normalize=True) * 100).round(2).to_dict()
            insights['avg_sentiment_score'] = df['sentiment_score'].mean()
        
        # By bank
        if 'bank' in df.columns:
            insights['by_bank'] = {}
            for bank in df['bank'].unique():
                bank_df = df[df['bank'] == bank]
                insights['by_bank'][bank] = {
                    'distribution': bank_df['sentiment_label'].value_counts().to_dict(),
                    'avg_score': round(bank_df['sentiment_score'].mean(), 4),
                    'count': len(bank_df)
                }
        
        # By rating
        if 'rating' in df.columns:
            insights['by_rating'] = {}
            for rating in sorted(df['rating'].unique()):
                rating_df = df[df['rating'] == rating]
                insights['by_rating'][int(rating)] = {
                    'distribution': rating_df['sentiment_label'].value_counts().to_dict(),
                    'avg_score': round(rating_df['sentiment_score'].mean(), 4),
                    'count': len(rating_df)
                }
        
        return insights

