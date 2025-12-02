"""
NLP Pipeline Module
Modular text processing pipeline with tokenization, stop-word removal, 
lemmatization, and normalization
"""

import logging
import re
from typing import List, Optional, Callable
import pandas as pd

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# NLTK for text processing
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.stem import WordNetLemmatizer
    from nltk.tag import pos_tag
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    logger.warning("NLTK not available. Some features may be limited.")

# spaCy for advanced NLP
try:
    import spacy
    from spacy.lang.en.stop_words import STOP_WORDS
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


class NLPipeline:
    """Modular NLP text processing pipeline"""
    
    def __init__(self, use_spacy: bool = True, use_nltk: bool = True):
        """
        Initialize NLP pipeline
        
        Args:
            use_spacy: Whether to use spaCy for advanced processing
            use_nltk: Whether to use NLTK for tokenization and lemmatization
        """
        self.use_spacy = use_spacy and SPACY_AVAILABLE
        self.use_nltk = use_nltk and NLTK_AVAILABLE
        
        # Initialize NLTK components
        if self.use_nltk:
            try:
                # Download required NLTK data
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                nltk.download('wordnet', quiet=True)
                nltk.download('averaged_perceptron_tagger', quiet=True)
                
                self.lemmatizer = WordNetLemmatizer()
                self.stop_words = set(stopwords.words('english'))
                logger.info("✓ NLTK components initialized")
            except Exception as e:
                logger.warning(f"NLTK initialization failed: {e}")
                self.use_nltk = False
        
        # Initialize spaCy
        if self.use_spacy:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("✓ spaCy model loaded")
            except OSError:
                logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
                self.use_spacy = False
                self.nlp = None
        
        logger.info(f"NLP pipeline initialized (spacy={self.use_spacy}, nltk={self.use_nltk})")
    
    def normalize_text(self, text: str) -> str:
        """
        Basic text normalization
        
        Args:
            text: Input text
            
        Returns:
            Normalized text
        """
        if not text or pd.isna(text):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?]', ' ', text)
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def tokenize_nltk(self, text: str) -> List[str]:
        """
        Tokenize text using NLTK
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        if not self.use_nltk or not text:
            return []
        
        try:
            tokens = word_tokenize(text)
            return tokens
        except Exception as e:
            logger.warning(f"Error in NLTK tokenization: {e}")
            return text.split()
    
    def tokenize_spacy(self, text: str) -> List[str]:
        """
        Tokenize text using spaCy
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        if not self.use_spacy or not text or not self.nlp:
            return []
        
        try:
            doc = self.nlp(text)
            tokens = [token.text for token in doc]
            return tokens
        except Exception as e:
            logger.warning(f"Error in spaCy tokenization: {e}")
            return text.split()
    
    def tokenize(self, text: str, method: str = 'spacy') -> List[str]:
        """
        Tokenize text using specified method
        
        Args:
            text: Input text
            method: 'spacy', 'nltk', or 'simple'
            
        Returns:
            List of tokens
        """
        if method == 'spacy' and self.use_spacy:
            return self.tokenize_spacy(text)
        elif method == 'nltk' and self.use_nltk:
            return self.tokenize_nltk(text)
        else:
            # Simple whitespace tokenization
            return text.split()
    
    def remove_stopwords(self, tokens: List[str], custom_stopwords: Optional[set] = None) -> List[str]:
        """
        Remove stop words from tokens
        
        Args:
            tokens: List of tokens
            custom_stopwords: Optional custom set of stop words
            
        Returns:
            List of tokens with stop words removed
        """
        if not tokens:
            return []
        
        # Combine default and custom stop words
        if self.use_spacy:
            stop_words = STOP_WORDS.copy()
        elif self.use_nltk:
            stop_words = self.stop_words.copy()
        else:
            stop_words = set()
        
        if custom_stopwords:
            stop_words.update(custom_stopwords)
        
        # Remove stop words
        filtered_tokens = [token for token in tokens if token.lower() not in stop_words]
        
        return filtered_tokens
    
    def lemmatize_nltk(self, tokens: List[str]) -> List[str]:
        """
        Lemmatize tokens using NLTK
        
        Args:
            tokens: List of tokens
            
        Returns:
            List of lemmatized tokens
        """
        if not self.use_nltk or not tokens:
            return tokens
        
        try:
            # Get POS tags for better lemmatization
            pos_tags = pos_tag(tokens)
            
            lemmatized = []
            for token, pos in pos_tags:
                # Map POS tags to WordNet POS tags
                pos_wn = self._get_wordnet_pos(pos)
                lemma = self.lemmatizer.lemmatize(token, pos=pos_wn)
                lemmatized.append(lemma)
            
            return lemmatized
        except Exception as e:
            logger.warning(f"Error in NLTK lemmatization: {e}")
            return tokens
    
    def lemmatize_spacy(self, text: str) -> List[str]:
        """
        Lemmatize text using spaCy
        
        Args:
            text: Input text
            
        Returns:
            List of lemmatized tokens
        """
        if not self.use_spacy or not text or not self.nlp:
            return []
        
        try:
            doc = self.nlp(text)
            lemmatized = [token.lemma_ for token in doc]
            return lemmatized
        except Exception as e:
            logger.warning(f"Error in spaCy lemmatization: {e}")
            return text.split()
    
    def lemmatize(self, tokens: List[str], method: str = 'spacy') -> List[str]:
        """
        Lemmatize tokens using specified method
        
        Args:
            tokens: List of tokens
            method: 'spacy' or 'nltk'
            
        Returns:
            List of lemmatized tokens
        """
        if method == 'spacy' and self.use_spacy:
            # spaCy works better with full text
            text = ' '.join(tokens)
            return self.lemmatize_spacy(text)
        elif method == 'nltk' and self.use_nltk:
            return self.lemmatize_nltk(tokens)
        else:
            return tokens
    
    def _get_wordnet_pos(self, treebank_tag: str) -> str:
        """
        Convert treebank POS tag to WordNet POS tag
        
        Args:
            treebank_tag: Treebank POS tag
            
        Returns:
            WordNet POS tag
        """
        if treebank_tag.startswith('J'):
            return 'a'  # Adjective
        elif treebank_tag.startswith('V'):
            return 'v'  # Verb
        elif treebank_tag.startswith('N'):
            return 'n'  # Noun
        elif treebank_tag.startswith('R'):
            return 'r'  # Adverb
        else:
            return 'n'  # Default to noun
    
    def process_text(self, text: str, 
                    normalize: bool = True,
                    tokenize: bool = True,
                    remove_stopwords: bool = True,
                    lemmatize: bool = True,
                    return_string: bool = False) -> List[str] | str:
        """
        Process text through the full pipeline
        
        Args:
            text: Input text
            normalize: Whether to normalize text
            tokenize: Whether to tokenize
            remove_stopwords: Whether to remove stop words
            lemmatize: Whether to lemmatize
            return_string: Whether to return as string (joined) or list
            
        Returns:
            Processed text as list of tokens or string
        """
        if not text or pd.isna(text):
            return "" if return_string else []
        
        # Normalize
        if normalize:
            text = self.normalize_text(text)
        
        # Tokenize
        if tokenize:
            tokens = self.tokenize(text, method='spacy' if self.use_spacy else 'nltk')
        else:
            tokens = text.split()
        
        # Remove stop words
        if remove_stopwords:
            tokens = self.remove_stopwords(tokens)
        
        # Lemmatize
        if lemmatize:
            tokens = self.lemmatize(tokens, method='spacy' if self.use_spacy else 'nltk')
        
        # Filter out empty tokens
        tokens = [t for t in tokens if t.strip()]
        
        if return_string:
            return ' '.join(tokens)
        else:
            return tokens
    
    def process_dataframe(self, df: pd.DataFrame, text_column: str = 'review',
                         processed_column: str = 'processed_text',
                         **process_kwargs) -> pd.DataFrame:
        """
        Process all texts in a DataFrame
        
        Args:
            df: DataFrame with text column
            text_column: Name of column containing text
            processed_column: Name of column to store processed text
            **process_kwargs: Additional arguments for process_text
            
        Returns:
            DataFrame with processed text column added
        """
        logger.info(f"Processing {len(df)} texts...")
        
        output_df = df.copy()
        
        # Process each text
        processed_texts = []
        for text in df[text_column]:
            processed = self.process_text(text, **process_kwargs)
            if isinstance(processed, list):
                processed = ' '.join(processed)
            processed_texts.append(processed)
        
        output_df[processed_column] = processed_texts
        
        logger.info("Text processing completed")
        return output_df

