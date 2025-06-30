import re
import nltk
from textblob import TextBlob
from collections import Counter
import config

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class ReviewAnalyzer:
    def __init__(self):
        self.fake_keywords = config.FAKE_KEYWORDS
        self.generic_phrases = config.GENERIC_PHRASES
    
    def analyze_single_review(self, review):
        """Analyze a single review and return authenticity score (0-100)"""
        text = (review.get('text', '') + ' ' + review.get('title', '')).lower()
        rating = review.get('rating', 0)
        
        # Initialize score (start assuming genuine)
        fake_score = 0
        signals = []
        
        # Signal 1: Keyword Analysis (30 points max)
        keyword_score = self._analyze_keywords(text)
        fake_score += keyword_score
        if keyword_score > 15:
            signals.append(f"Excessive promotional language ({keyword_score}/30 points)")
        
        # Signal 2: Length Analysis (20 points max)
        length_score = self._analyze_length(text)
        fake_score += length_score
        if length_score > 10:
            signals.append(f"Suspicious review length ({length_score}/20 points)")
        
        # Signal 3: Sentiment vs Rating Mismatch (25 points max)
        sentiment_score = self._analyze_sentiment_rating_match(text, rating)
        fake_score += sentiment_score
        if sentiment_score > 12:
            signals.append(f"Sentiment-rating mismatch ({sentiment_score}/25 points)")
        
        # Signal 4: Generic Content (15 points max)
        generic_score = self._analyze_generic_content(text)
        fake_score += generic_score
        if generic_score > 7:
            signals.append(f"Too generic/template-like ({generic_score}/15 points)")
        
        # Signal 5: Verification Status (10 points max)
        verification_score = self._analyze_verification(review)
        fake_score += verification_score
        if verification_score > 0:
            signals.append(f"Not verified purchase (+{verification_score} points)")
        
        # Cap at 100
        fake_score = min(fake_score, 100)
        
        return {
            'fake_score': fake_score,
            'is_suspicious': fake_score >= config.FAKE_THRESHOLD,
            'signals': signals,
            'analysis': {
                'keyword_score': keyword_score,
                'length_score': length_score,
                'sentiment_score': sentiment_score,
                'generic_score': generic_score,
                'verification_score': verification_score
            }
        }
    
    def _analyze_keywords(self, text):
        """Check for fake review keywords"""
        score = 0
        fake_count = sum(1 for keyword in self.fake_keywords if keyword in text)
        
        # More suspicious keywords = higher score
        if fake_count >= 3:
            score = 30
        elif fake_count == 2:
            score = 20
        elif fake_count == 1:
            score = 10
        
        return score
    
    def _analyze_length(self, text):
        """Analyze review length for suspicion"""
        word_count = len(text.split())
        
        # Very short reviews (under 10 words) can be fake
        if word_count < 10:
            return 15
        # Very long reviews (over 200 words) can also be fake
        elif word_count > 200:
            return 10
        
        return 0
    
    def _analyze_sentiment_rating_match(self, text, rating):
        """Check if sentiment matches the star rating"""
        if not text or rating == 0:
            return 5  # Missing data is slightly suspicious
        
        # Get sentiment polarity (-1 to 1)
        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity
        
        # Convert rating to expected sentiment range
        # 1-2 stars = negative (-1 to -0.3)
        # 3 stars = neutral (-0.3 to 0.3)  
        # 4-5 stars = positive (0.3 to 1)
        
        expected_sentiment = None
        if rating <= 2:
            expected_sentiment = 'negative'
        elif rating == 3:
            expected_sentiment = 'neutral'
        else:  # 4-5 stars
            expected_sentiment = 'positive'
        
        actual_sentiment = None
        if sentiment < -0.3:
            actual_sentiment = 'negative'
        elif sentiment > 0.3:
            actual_sentiment = 'positive'
        else:
            actual_sentiment = 'neutral'
        
        # Check for mismatch
        if expected_sentiment != actual_sentiment:
            # Big mismatches are more suspicious
            if (expected_sentiment == 'positive' and actual_sentiment == 'negative') or \
               (expected_sentiment == 'negative' and actual_sentiment == 'positive'):
                return 25
            else:
                return 15
        
        return 0
    
    def _analyze_generic_content(self, text):
        """Check for generic/template phrases"""
        generic_count = sum(1 for phrase in self.generic_phrases if phrase in text)
        
        if generic_count >= 3:
            return 15
        elif generic_count == 2:
            return 10
        elif generic_count == 1:
            return 5
        
        return 0
    
    def _analyze_verification(self, review):
        """Check verification status"""
        if not review.get('verified_purchase', True):
            return 10
        return 0
    
    def analyze_product_reviews(self, reviews):
        """Analyze all reviews for a product"""
        if len(reviews) < config.MIN_REVIEWS_FOR_ANALYSIS:
            return {
                'error': f'Need at least {config.MIN_REVIEWS_FOR_ANALYSIS} reviews for analysis',
                'review_count': len(reviews)
            }
        
        analyzed_reviews = []
        fake_count = 0
        total_score = 0
        
        for review in reviews:
            analysis = self.analyze_single_review(review)
            analyzed_reviews.append({
                'review': review,
                'analysis': analysis
            })
            
            if analysis['is_suspicious']:
                fake_count += 1
            
            total_score += analysis['fake_score']
        
        # Calculate metrics
        fake_percentage = (fake_count / len(reviews)) * 100
        average_fake_score = total_score / len(reviews)
        
        # Determine grade
        grade = self._calculate_grade(fake_percentage)
        
        # Calculate adjusted rating
        genuine_reviews = [r for r in analyzed_reviews if not r['analysis']['is_suspicious']]
        if genuine_reviews:
            adjusted_rating = sum(r['review']['rating'] for r in genuine_reviews) / len(genuine_reviews)
        else:
            adjusted_rating = 0
        
        return {
            'total_reviews': len(reviews),
            'fake_count': fake_count,
            'fake_percentage': fake_percentage,
            'average_fake_score': average_fake_score,
            'grade': grade,
            'adjusted_rating': round(adjusted_rating, 1),
            'analyzed_reviews': analyzed_reviews,
            'suspicious_reviews': [r for r in analyzed_reviews if r['analysis']['is_suspicious']]
        }
    
    def _calculate_grade(self, fake_percentage):
        """Calculate letter grade based on fake percentage"""
        for grade, (min_pct, max_pct) in config.GRADE_THRESHOLDS.items():
            if min_pct <= fake_percentage < max_pct:
                return grade
        return 'F'  # Default to F if something goes wrong