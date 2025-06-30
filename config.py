PROWEBSCRAPER_EMAIL = "your_email@example.com"  # Your ProWebScraper account email
PROWEBSCRAPER_PASSWORD = "your_password"        # Your ProWebScraper password

USE_DEMO_DATA = True

FAKE_THRESHOLD = 70  
MIN_REVIEWS_FOR_ANALYSIS = 5

# Grading Scale
GRADE_THRESHOLDS = {
    'A': (0, 10),      # 0-10% fake reviews
    'B': (10, 20),     # 10-20% fake reviews  
    'C': (20, 35),     # 20-35% fake reviews
    'D': (35, 50),     # 35-50% fake reviews
    'F': (50, 100)     # 50%+ fake reviews
}

# Keywords that indicate fake reviews
FAKE_KEYWORDS = [
    'amazing', 'perfect', 'best ever', 'must buy', 'highly recommend',
    'five stars', '5 stars', 'exceeded expectations', 'blown away',
    'life changing', 'game changer', 'absolutely love', 'fantastic'
]

GENERIC_PHRASES = [
    'great product', 'good quality', 'fast shipping', 'as described',
    'would recommend', 'happy with purchase', 'good value', 'satisfied'
]
