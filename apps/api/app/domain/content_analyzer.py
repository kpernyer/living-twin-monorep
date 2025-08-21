"""Advanced content analysis for AI agent results."""

import re
import logging
from typing import Dict, List, Tuple, Optional, Set
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ContentAnalysis:
    """Result of content analysis."""
    
    # Basic metrics
    word_count: int
    sentence_count: int
    paragraph_count: int
    
    # Sentiment analysis
    sentiment_score: float  # -1.0 to 1.0
    sentiment_label: str  # "positive", "negative", "neutral"
    confidence: float  # 0.0 to 1.0
    
    # Keyword analysis
    keywords_found: List[str]
    keyword_frequency: Dict[str, int]
    keyword_relevance: Dict[str, float]
    
    # Theme extraction
    themes: List[str]
    theme_confidence: Dict[str, float]
    
    # Entity extraction
    entities: Dict[str, List[str]]  # category -> entities
    entity_confidence: Dict[str, float]
    
    # Content quality
    readability_score: float
    content_type: str  # "news", "opinion", "technical", "marketing"
    
    # Metadata
    analysis_timestamp: datetime
    processing_time_ms: float


class ContentAnalyzer:
    """Advanced content analyzer for extracting insights from text."""
    
    def __init__(self):
        # Sentiment dictionaries
        self.positive_words = {
            'good', 'great', 'excellent', 'amazing', 'positive', 'success', 'growth', 'innovation',
            'breakthrough', 'revolutionary', 'leading', 'advanced', 'superior', 'outstanding',
            'promising', 'exciting', 'impressive', 'remarkable', 'exceptional', 'brilliant',
            'innovative', 'cutting-edge', 'state-of-the-art', 'game-changing', 'disruptive',
            'profitable', 'efficient', 'effective', 'powerful', 'fast', 'reliable', 'secure',
            'scalable', 'flexible', 'user-friendly', 'intuitive', 'seamless', 'integrated'
        }
        
        self.negative_words = {
            'bad', 'terrible', 'awful', 'negative', 'failure', 'decline', 'problem', 'issue',
            'concern', 'worry', 'risk', 'threat', 'danger', 'crisis', 'disaster', 'catastrophe',
            'disappointing', 'frustrating', 'annoying', 'difficult', 'complex', 'expensive',
            'slow', 'unreliable', 'insecure', 'vulnerable', 'outdated', 'obsolete', 'redundant',
            'inefficient', 'ineffective', 'weak', 'limited', 'restricted', 'complicated',
            'confusing', 'difficult', 'challenging', 'problematic', 'troublesome'
        }
        
        # Theme keywords
        self.theme_keywords = {
            'artificial_intelligence': {
                'ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning',
                'neural networks', 'algorithm', 'automation', 'robotics', 'chatbot', 'llm',
                'gpt', 'transformer', 'natural language processing', 'nlp', 'computer vision'
            },
            'cloud_computing': {
                'cloud', 'aws', 'azure', 'google cloud', 'saas', 'paas', 'iaas',
                'serverless', 'microservices', 'container', 'docker', 'kubernetes',
                'virtualization', 'distributed computing', 'edge computing'
            },
            'cybersecurity': {
                'security', 'cybersecurity', 'hacking', 'breach', 'vulnerability',
                'encryption', 'authentication', 'firewall', 'malware', 'phishing',
                'zero-day', 'penetration testing', 'compliance', 'gdpr', 'privacy'
            },
            'fintech': {
                'fintech', 'blockchain', 'cryptocurrency', 'bitcoin', 'ethereum',
                'digital payment', 'mobile banking', 'insurtech', 'regtech',
                'robo-advisor', 'crowdfunding', 'peer-to-peer lending'
            },
            'healthcare_tech': {
                'healthtech', 'telemedicine', 'digital health', 'wearables',
                'medical device', 'diagnostic', 'treatment', 'patient care',
                'healthcare ai', 'precision medicine', 'genomics'
            },
            'ecommerce': {
                'ecommerce', 'online retail', 'digital commerce', 'marketplace',
                'payment processing', 'inventory management', 'supply chain',
                'logistics', 'fulfillment', 'customer experience'
            },
            'startup_ecosystem': {
                'startup', 'venture capital', 'funding', 'investment', 'unicorn',
                'accelerator', 'incubator', 'pitch', 'demo day', 'series a',
                'seed funding', 'angel investor', 'exit', 'ipo', 'acquisition'
            },
            'digital_transformation': {
                'digital transformation', 'digitalization', 'automation',
                'process improvement', 'workflow', 'enterprise software',
                'erp', 'crm', 'business intelligence', 'analytics', 'data'
            }
        }
        
        # Entity categories
        self.entity_patterns = {
            'companies': r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc|Corp|LLC|Ltd|Company|Technologies|Systems|Solutions)\b',
            'products': r'\b[A-Z][a-zA-Z0-9\s]+(?:Pro|Plus|Max|Ultra|Elite|Premium|Enterprise|Cloud|AI|ML)\b',
            'technologies': r'\b[A-Z][a-zA-Z0-9]+(?:\.js|\.py|\.net|\.io|\.ai|\.tech)\b',
            'currencies': r'\b(?:USD|EUR|GBP|JPY|CNY|BTC|ETH|USDT|USDC)\b',
            'percentages': r'\b\d+(?:\.\d+)?%\b',
            'monetary': r'\$[\d,]+(?:\.\d{2})?(?:\s+(?:million|billion|trillion))?\b',
        }
    
    def analyze_content(self, text: str, title: str = "", keywords: List[str] = None) -> ContentAnalysis:
        """Perform comprehensive content analysis."""
        import time
        start_time = time.time()
        
        # Basic text preprocessing
        clean_text = self._preprocess_text(text)
        title_clean = self._preprocess_text(title) if title else ""
        
        # Basic metrics
        word_count = len(clean_text.split())
        sentence_count = len(re.split(r'[.!?]+', clean_text))
        paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
        
        # Sentiment analysis
        sentiment_score, sentiment_label, confidence = self._analyze_sentiment(clean_text, title_clean)
        
        # Keyword analysis
        keywords_found, keyword_frequency, keyword_relevance = self._analyze_keywords(
            clean_text, title_clean, keywords or []
        )
        
        # Theme extraction
        themes, theme_confidence = self._extract_themes(clean_text, title_clean)
        
        # Entity extraction
        entities, entity_confidence = self._extract_entities(clean_text, title_clean)
        
        # Content quality
        readability_score = self._calculate_readability(clean_text)
        content_type = self._classify_content_type(clean_text, title_clean)
        
        processing_time = (time.time() - start_time) * 1000
        
        return ContentAnalysis(
            word_count=word_count,
            sentence_count=sentence_count,
            paragraph_count=paragraph_count,
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
            confidence=confidence,
            keywords_found=keywords_found,
            keyword_frequency=keyword_frequency,
            keyword_relevance=keyword_relevance,
            themes=themes,
            theme_confidence=theme_confidence,
            entities=entities,
            entity_confidence=entity_confidence,
            readability_score=readability_score,
            content_type=content_type,
            analysis_timestamp=datetime.utcnow(),
            processing_time_ms=processing_time
        )
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and normalize text for analysis."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\!\?\,\;\:\-\(\)]', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _analyze_sentiment(self, text: str, title: str = "") -> Tuple[float, str, float]:
        """Analyze sentiment with confidence scoring."""
        combined_text = f"{title} {text}"
        words = combined_text.split()
        
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            return 0.0, "neutral", 0.0
        
        # Calculate sentiment score (-1 to 1)
        sentiment_score = (positive_count - negative_count) / total_sentiment_words
        
        # Determine label
        if sentiment_score > 0.1:
            sentiment_label = "positive"
        elif sentiment_score < -0.1:
            sentiment_label = "negative"
        else:
            sentiment_label = "neutral"
        
        # Calculate confidence based on number of sentiment words
        confidence = min(1.0, total_sentiment_words / 10.0)  # More words = higher confidence
        
        return sentiment_score, sentiment_label, confidence
    
    def _analyze_keywords(self, text: str, title: str, target_keywords: List[str]) -> Tuple[List[str], Dict[str, int], Dict[str, float]]:
        """Analyze keyword presence and relevance."""
        combined_text = f"{title} {text}"
        words = combined_text.split()
        word_freq = Counter(words)
        
        keywords_found = []
        keyword_frequency = {}
        keyword_relevance = {}
        
        for keyword in target_keywords:
            keyword_lower = keyword.lower()
            
            # Check for exact matches and partial matches
            matches = 0
            for word in words:
                if keyword_lower in word or word in keyword_lower:
                    matches += 1
            
            if matches > 0:
                keywords_found.append(keyword)
                keyword_frequency[keyword] = matches
                
                # Calculate relevance score (0-1)
                relevance = min(1.0, matches / 5.0)  # Normalize by expected frequency
                keyword_relevance[keyword] = relevance
        
        return keywords_found, keyword_frequency, keyword_relevance
    
    def _extract_themes(self, text: str, title: str) -> Tuple[List[str], Dict[str, float]]:
        """Extract themes from content."""
        combined_text = f"{title} {text}"
        words = set(combined_text.split())
        
        themes = []
        theme_confidence = {}
        
        for theme_name, theme_keywords in self.theme_keywords.items():
            matches = len(words.intersection(theme_keywords))
            
            if matches >= 2:  # Require at least 2 keyword matches
                themes.append(theme_name)
                confidence = min(1.0, matches / len(theme_keywords))
                theme_confidence[theme_name] = confidence
        
        return themes, theme_confidence
    
    def _extract_entities(self, text: str, title: str) -> Tuple[Dict[str, List[str]], Dict[str, float]]:
        """Extract named entities from content."""
        combined_text = f"{title} {text}"
        
        entities = defaultdict(list)
        entity_confidence = {}
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            if matches:
                entities[entity_type] = list(set(matches))  # Remove duplicates
                entity_confidence[entity_type] = min(1.0, len(matches) / 5.0)
        
        return dict(entities), entity_confidence
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate Flesch Reading Ease score."""
        sentences = re.split(r'[.!?]+', text)
        words = text.split()
        syllables = self._count_syllables(text)
        
        if len(sentences) == 0 or len(words) == 0:
            return 0.0
        
        # Flesch Reading Ease formula
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = syllables / len(words)
        
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        return max(0.0, min(100.0, score))  # Clamp between 0-100
    
    def _count_syllables(self, text: str) -> int:
        """Estimate syllable count in text."""
        # Simple syllable estimation
        text = text.lower()
        count = 0
        vowels = "aeiouy"
        on_vowel = False
        
        for char in text:
            is_vowel = char in vowels
            if is_vowel and not on_vowel:
                count += 1
            on_vowel = is_vowel
        
        return count
    
    def _classify_content_type(self, text: str, title: str) -> str:
        """Classify the type of content."""
        combined_text = f"{title} {text}".lower()
        
        # Content type indicators
        type_indicators = {
            'news': ['announced', 'reported', 'according to', 'said', 'revealed', 'published'],
            'opinion': ['i think', 'in my opinion', 'believe', 'argue', 'suggest', 'recommend'],
            'technical': ['implementation', 'architecture', 'algorithm', 'api', 'framework', 'protocol'],
            'marketing': ['buy now', 'limited time', 'special offer', 'discount', 'free trial', 'sign up']
        }
        
        scores = {}
        for content_type, indicators in type_indicators.items():
            score = sum(1 for indicator in indicators if indicator in combined_text)
            scores[content_type] = score
        
        # Return the type with highest score, default to 'news'
        if scores:
            return max(scores, key=scores.get)
        return 'news'
    
    def generate_summary(self, analysis: ContentAnalysis) -> str:
        """Generate a human-readable summary of the analysis."""
        summary_parts = []
        
        # Basic info
        summary_parts.append(f"Content Analysis Summary:")
        summary_parts.append(f"- Word count: {analysis.word_count}")
        summary_parts.append(f"- Sentences: {analysis.sentence_count}")
        summary_parts.append(f"- Paragraphs: {analysis.paragraph_count}")
        
        # Sentiment
        summary_parts.append(f"- Sentiment: {analysis.sentiment_label} (score: {analysis.sentiment_score:.2f}, confidence: {analysis.confidence:.2f})")
        
        # Keywords
        if analysis.keywords_found:
            summary_parts.append(f"- Keywords found: {', '.join(analysis.keywords_found)}")
        
        # Themes
        if analysis.themes:
            summary_parts.append(f"- Themes: {', '.join(analysis.themes)}")
        
        # Entities
        if analysis.entities:
            for entity_type, entities in analysis.entities.items():
                summary_parts.append(f"- {entity_type.title()}: {', '.join(entities[:3])}")  # Show first 3
        
        # Quality
        summary_parts.append(f"- Readability: {analysis.readability_score:.1f}/100")
        summary_parts.append(f"- Content type: {analysis.content_type}")
        
        return '\n'.join(summary_parts)
