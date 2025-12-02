"""
Thematic Analysis Module
Identifies and groups recurring review topics using keyword extraction and clustering
"""

import logging
from typing import Dict, List, Optional, Tuple, Set
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import re

# TF-IDF and clustering
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation

# spaCy for NLP
try:
    import spacy
    from spacy.lang.en.stop_words import STOP_WORDS
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

logger = logging.getLogger(__name__)

# Log spaCy availability after logger is initialized
if not SPACY_AVAILABLE:
    logger.warning("spaCy not available. Install with: python -m spacy download en_core_web_sm")


class ThematicAnalyzer:
    """Identifies themes and topics in reviews"""
    
    def __init__(self, n_themes: int = 5, use_spacy: bool = True, 
                 min_keyword_freq: int = 3, max_keywords_per_theme: int = 10):
        """
        Initialize thematic analyzer
        
        Args:
            n_themes: Number of themes to identify per bank
            use_spacy: Whether to use spaCy for advanced NLP (requires en_core_web_sm model)
            min_keyword_freq: Minimum frequency for keywords to be considered
            max_keywords_per_theme: Maximum number of keywords to extract per theme
        """
        self.n_themes = n_themes
        self.use_spacy = use_spacy and SPACY_AVAILABLE
        self.min_keyword_freq = min_keyword_freq
        self.max_keywords_per_theme = max_keywords_per_theme
        
        # Initialize spaCy if available
        if self.use_spacy:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("✓ spaCy model loaded successfully")
            except OSError:
                logger.warning("spaCy model 'en_core_web_sm' not found. Install with: python -m spacy download en_core_web_sm")
                self.use_spacy = False
                self.nlp = None
        else:
            self.nlp = None
        
        # Theme definitions and keywords (banking-specific)
        self.theme_keywords = {
            'Account Access Problems': [
                'login', 'password', 'account', 'access', 'unable', 'cannot', 'failed',
                'error', 'otp', 'verification', 'authenticate', 'locked', 'blocked',
                'open account', 'register', 'sign up', 'selfie', 'verify'
            ],
            'Transaction Speed & Reliability': [
                'slow', 'fast', 'speed', 'transaction', 'transfer', 'payment',
                'delay', 'pending', 'timeout', 'failed transaction', 'processing',
                'instant', 'quick', 'waiting', 'hang', 'freeze', 'stuck'
            ],
            'User Interface & Experience': [
                'ui', 'interface', 'design', 'user friendly', 'easy', 'simple',
                'beautiful', 'ugly', 'confusing', 'layout', 'navigation', 'button',
                'screen', 'display', 'visual', 'aesthetic', 'intuitive'
            ],
            'Customer Support Responsiveness': [
                'support', 'customer service', 'help', 'response', 'reply',
                'contact', 'assistance', 'complaint', 'no reply', 'unresponsive',
                'email', 'call', 'service', 'helpful', 'ignore'
            ],
            'Feature Requests': [
                'feature', 'add', 'missing', 'need', 'want', 'should have',
                'request', 'suggestion', 'improve', 'enhance', 'update',
                'new feature', 'option', 'functionality', 'capability'
            ],
            'Security & Trust': [
                'security', 'safe', 'secure', 'trust', 'privacy', 'data',
                'protection', 'hack', 'fraud', 'scam', 'reliable', 'trustworthy'
            ],
            'App Performance & Stability': [
                'crash', 'bug', 'glitch', 'error', 'not working', 'broken',
                'freeze', 'lag', 'performance', 'stable', 'reliable', 'update',
                'version', 'compatibility', 'install'
            ]
        }
        
        logger.info(f"Thematic analyzer initialized (n_themes={n_themes}, use_spacy={self.use_spacy})")
    
    def extract_keywords_tfidf(self, texts: List[str], max_features: int = 100) -> Dict[str, float]:
        """
        Extract keywords using TF-IDF
        
        Args:
            texts: List of review texts
            max_features: Maximum number of features to extract
            
        Returns:
            Dictionary mapping keywords to TF-IDF scores
        """
        if not texts:
            return {}
        
        try:
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                max_features=max_features,
                stop_words='english',
                ngram_range=(1, 2),  # Include unigrams and bigrams
                min_df=2,  # Minimum document frequency
                max_df=0.95  # Maximum document frequency
            )
            
            # Fit and transform
            tfidf_matrix = vectorizer.fit_transform(texts)
            feature_names = vectorizer.get_feature_names_out()
            
            # Calculate average TF-IDF scores
            scores = np.mean(tfidf_matrix.toarray(), axis=0)
            
            # Create keyword dictionary
            keywords = dict(zip(feature_names, scores))
            
            # Sort by score
            keywords = dict(sorted(keywords.items(), key=lambda x: x[1], reverse=True))
            
            logger.info(f"Extracted {len(keywords)} keywords using TF-IDF")
            return keywords
            
        except Exception as e:
            logger.error(f"Error in TF-IDF extraction: {e}")
            return {}
    
    def extract_keywords_spacy(self, texts: List[str]) -> Dict[str, float]:
        """
        Extract keywords using spaCy (nouns, adjectives, key phrases)
        
        Args:
            texts: List of review texts
            
        Returns:
            Dictionary mapping keywords to importance scores
        """
        if not self.use_spacy or not texts:
            return {}
        
        keyword_scores = Counter()
        
        try:
            for text in texts:
                if not text or pd.isna(text):
                    continue
                
                doc = self.nlp(text.lower())
                
                # Extract important words (nouns, adjectives, verbs)
                for token in doc:
                    # Skip stop words, punctuation, and very short words
                    if (token.is_stop or token.is_punct or len(token.text) < 3 or 
                        token.text in STOP_WORDS):
                        continue
                    
                    # Focus on nouns, adjectives, and verbs
                    if token.pos_ in ['NOUN', 'ADJ', 'VERB']:
                        keyword_scores[token.lemma_] += 1
                
                # Extract noun phrases
                for chunk in doc.noun_chunks:
                    if len(chunk.text.split()) <= 3:  # Max 3-word phrases
                        phrase = chunk.text.lower().strip()
                        if len(phrase) > 3:
                            keyword_scores[phrase] += 1
            
            # Normalize scores
            total = sum(keyword_scores.values())
            if total > 0:
                keywords = {k: v/total for k, v in keyword_scores.items()}
            else:
                keywords = {}
            
            logger.info(f"Extracted {len(keywords)} keywords using spaCy")
            return keywords
            
        except Exception as e:
            logger.error(f"Error in spaCy extraction: {e}")
            return {}
    
    def extract_keywords(self, texts: List[str], method: str = 'both') -> Dict[str, float]:
        """
        Extract keywords using specified method(s)
        
        Args:
            texts: List of review texts
            method: 'tfidf', 'spacy', or 'both'
            
        Returns:
            Dictionary mapping keywords to scores
        """
        all_keywords = {}
        
        if method in ['tfidf', 'both']:
            tfidf_keywords = self.extract_keywords_tfidf(texts)
            all_keywords.update(tfidf_keywords)
        
        if method in ['spacy', 'both']:
            spacy_keywords = self.extract_keywords_spacy(texts)
            # Combine scores (average if both methods used)
            if method == 'both':
                for k, v in spacy_keywords.items():
                    if k in all_keywords:
                        all_keywords[k] = (all_keywords[k] + v) / 2
                    else:
                        all_keywords[k] = v
            else:
                all_keywords.update(spacy_keywords)
        
        # Filter by minimum frequency
        if texts and len(texts) > 0:
            min_threshold = self.min_keyword_freq / len(texts)
            filtered_keywords = {
                k: v for k, v in all_keywords.items() 
                if v >= min_threshold
            }
        else:
            filtered_keywords = {}
        
        return filtered_keywords
    
    def match_keywords_to_themes(self, keywords: Dict[str, float]) -> Dict[str, List[Tuple[str, float]]]:
        """
        Match extracted keywords to predefined themes
        
        Args:
            keywords: Dictionary of keywords and their scores
            
        Returns:
            Dictionary mapping theme names to lists of (keyword, score) tuples
        """
        theme_matches = defaultdict(list)
        
        keyword_lower = {k.lower(): (k, v) for k, v in keywords.items()}
        
        for theme, theme_keywords in self.theme_keywords.items():
            for theme_keyword in theme_keywords:
                theme_keyword_lower = theme_keyword.lower()
                
                # Check for exact matches or substring matches
                for kw_lower, (kw_original, score) in keyword_lower.items():
                    if (theme_keyword_lower in kw_lower or kw_lower in theme_keyword_lower):
                        theme_matches[theme].append((kw_original, score))
        
        # Sort by score and limit
        for theme in theme_matches:
            theme_matches[theme].sort(key=lambda x: x[1], reverse=True)
            theme_matches[theme] = theme_matches[theme][:self.max_keywords_per_theme]
        
        return dict(theme_matches)
    
    def cluster_themes(self, texts: List[str], n_clusters: Optional[int] = None) -> Dict[int, List[str]]:
        """
        Cluster texts into themes using K-means and LDA
        
        Args:
            texts: List of review texts
            n_clusters: Number of clusters (defaults to self.n_themes)
            
        Returns:
            Dictionary mapping cluster IDs to lists of texts
        """
        if not texts or len(texts) < 2:
            return {}
        
        n_clusters = n_clusters or min(self.n_themes, len(texts))
        n_clusters = min(n_clusters, len(texts))  # Can't have more clusters than texts
        
        try:
            # Create TF-IDF vectors
            vectorizer = TfidfVectorizer(
                max_features=100,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=2
            )
            tfidf_matrix = vectorizer.fit_transform(texts)
            
            # K-means clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(tfidf_matrix)
            
            # Group texts by cluster
            clusters = defaultdict(list)
            for idx, label in enumerate(cluster_labels):
                clusters[label].append(texts[idx])
            
            logger.info(f"Clustered {len(texts)} texts into {len(clusters)} themes")
            return dict(clusters)
            
        except Exception as e:
            logger.error(f"Error in clustering: {e}")
            return {}
    
    def identify_themes(self, texts: List[str], bank_name: str = "") -> Dict[str, Dict]:
        """
        Identify themes for a set of reviews
        
        Args:
            texts: List of review texts
            bank_name: Name of bank (for logging)
            
        Returns:
            Dictionary with theme information
        """
        if not texts:
            return {}
        
        logger.info(f"Identifying themes for {len(texts)} reviews" + 
                   (f" (Bank: {bank_name})" if bank_name else ""))
        
        # Extract keywords
        keywords = self.extract_keywords(texts, method='both')
        
        # Match keywords to themes
        theme_matches = self.match_keywords_to_themes(keywords)
        
        # Cluster texts for additional insights
        clusters = self.cluster_themes(texts, n_clusters=self.n_themes)
        
        # Build theme results
        themes = {}
        
        # Use predefined themes that have matches
        for theme_name, matched_keywords in theme_matches.items():
            if matched_keywords:  # Only include themes with keyword matches
                themes[theme_name] = {
                    'keywords': [kw for kw, _ in matched_keywords],
                    'keyword_scores': {kw: score for kw, score in matched_keywords},
                    'review_count': 0,  # Will be updated when classifying individual reviews
                    'logic': f"Matched {len(matched_keywords)} keywords related to {theme_name.lower()}"
                }
        
        # If we have fewer themes than requested, add cluster-based themes
        if len(themes) < self.n_themes and clusters:
            cluster_idx = len(themes)
            for cluster_id, cluster_texts in list(clusters.items())[:self.n_themes - len(themes)]:
                # Extract keywords for this cluster
                cluster_keywords = self.extract_keywords(cluster_texts, method='tfidf')
                top_keywords = sorted(cluster_keywords.items(), key=lambda x: x[1], reverse=True)[:5]
                
                theme_name = f"Cluster Theme {cluster_id + 1}"
                themes[theme_name] = {
                    'keywords': [kw for kw, _ in top_keywords],
                    'keyword_scores': dict(top_keywords),
                    'review_count': len(cluster_texts),
                    'logic': f"Identified via K-means clustering with top keywords: {', '.join([kw for kw, _ in top_keywords[:3]])}"
                }
                cluster_idx += 1
        
        logger.info(f"Identified {len(themes)} themes")
        return themes
    
    def classify_review_theme(self, text: str, themes: Dict[str, Dict]) -> List[str]:
        """
        Classify a single review into one or more themes
        
        Args:
            text: Review text
            themes: Dictionary of themes with keywords
            
        Returns:
            List of theme names that match the review
        """
        if not text or pd.isna(text) or not themes:
            return []
        
        text_lower = text.lower()
        matched_themes = []
        
        for theme_name, theme_data in themes.items():
            keywords = theme_data.get('keywords', [])
            
            # Check if any keywords appear in the text
            matches = sum(1 for kw in keywords if kw.lower() in text_lower)
            
            # If at least one keyword matches, assign theme
            if matches > 0:
                matched_themes.append(theme_name)
        
        return matched_themes if matched_themes else ['Uncategorized']
    
    def analyze_dataframe(self, df: pd.DataFrame, text_column: str = 'review',
                         bank_column: str = 'bank') -> pd.DataFrame:
        """
        Analyze themes for all reviews in a DataFrame
        
        Args:
            df: DataFrame with review texts
            text_column: Name of column containing review text
            bank_column: Name of column containing bank name
            
        Returns:
            DataFrame with theme columns added
        """
        logger.info(f"Analyzing themes for {len(df)} reviews...")
        
        output_df = df.copy()
        output_df['identified_themes'] = None
        output_df['primary_theme'] = None
        
        # Analyze themes per bank
        all_themes = {}
        
        for bank in df[bank_column].unique():
            bank_df = df[df[bank_column] == bank]
            bank_texts = bank_df[text_column].tolist()
            
            # Identify themes for this bank
            themes = self.identify_themes(bank_texts, bank_name=bank)
            all_themes[bank] = themes
            
            # Classify each review
            for idx in bank_df.index:
                text = bank_df.loc[idx, text_column]
                matched_themes = self.classify_review_theme(text, themes)
                
                if matched_themes:
                    output_df.loc[idx, 'identified_themes'] = '; '.join(matched_themes)
                    output_df.loc[idx, 'primary_theme'] = matched_themes[0]
        
        # Update theme review counts
        for bank, themes in all_themes.items():
            bank_df = output_df[output_df[bank_column] == bank]
            for theme_name in themes.keys():
                count = bank_df['primary_theme'].eq(theme_name).sum()
                themes[theme_name]['review_count'] = count
        
        logger.info("Theme analysis completed")
        return output_df, all_themes

