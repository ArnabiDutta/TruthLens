import requests
import pandas as pd
import re
from transformers import RobertaTokenizer, RobertaModel
import torch
import numpy as np

# Load tokenizer & model
tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
model = RobertaModel.from_pretrained('roberta-base')
model.eval()

def fetch_reviews(product_url: str) -> pd.DataFrame:
    resp = requests.get(
        'http://localhost:5000/',
        params={'url': product_url}, timeout=30
    )
    data = resp.json()
    df = pd.DataFrame(data)
    return df

# Text cleaning
def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

# Transform & extract features
def score_text(text: str) -> float:
    inputs = tokenizer(clean_text(text),
                       return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    cls_emb = outputs.last_hidden_state[:, 0].numpy()
    raw = np.linalg.norm(cls_emb)
    # Calibrate raw to 0-100
    calibrated = min(100, max(0, (raw - 5) * 12))
    return float(calibrated)

# Additional engineered features
def extra_features(df: pd.DataFrame) -> pd.DataFrame:
    df['length'] = df['content'].apply(len)
    keywords = ['best ever', 'must buy']
    df['keyword_flag'] = df['content'].apply(
        lambda t: any(k in t.lower() for k in keywords)
    )
    return df

# Full pipeline
def process_reviews(url: str) -> pd.DataFrame:
    df = fetch_reviews(url)
    df = extra_features(df)
    df['score'] = df['content'].apply(score_text)
    df['flagged'] = df['score'] >= 70
    return df
