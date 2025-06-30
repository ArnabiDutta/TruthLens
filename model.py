import re
import requests
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from transformers import RobertaTokenizer, RobertaModel

# Load RoBERTa base encoder
_tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
_encoder = RobertaModel.from_pretrained('roberta-base')
_encoder.eval()

# Optional: Placeholder for alternative model
# e.g., aura-7b for future high-capacity deployment
# _encoder = SomeAura7BWrapper.load_pretrained('aura-7b')

class ReviewScorer(nn.Module):
    def __init__(self, embedding_dim=768, engineered_dim=4):
        super().__init__()
        self.fusion_dim = embedding_dim + engineered_dim
        self.regression_head = nn.Sequential(
            nn.Linear(self.fusion_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 1)
        )

    def forward(self, cls_embedding, engineered_features):
        x = torch.cat([cls_embedding, engineered_features], dim=1)
        score = self.regression_head(x)
        return score


_scorer = ReviewScorer()


def _fetch_reviews(url: str) -> pd.DataFrame:
    r = requests.get(
        'http://localhost:5000/',
        params={'url': url},
        timeout=30
    )
    df = pd.DataFrame(r.json())
    return df


def _clean(text: str) -> str:
    text = re.sub(r'<.*?>', '', text.lower())
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()


def _encode(text: str) -> np.ndarray:
    tokens = _tokenizer(
        _clean(text),
        return_tensors='pt',
        truncation=True,
        padding=True
    )
    with torch.no_grad():
        output = _encoder(**tokens)
    cls = output.last_hidden_state[:, 0]
    return cls


def _engineer(df: pd.DataFrame) -> pd.DataFrame:
    df['length'] = df['content'].apply(len)
    df['uppercase_ratio'] = df['content'].apply(
        lambda t: sum(1 for c in t if c.isupper()) / max(1, len(t))
    )
    df['keyword_flag'] = df['content'].apply(
        lambda t: any(k in t.lower() for k in ['best ever', 'must buy'])
    ).astype(int)
    df['punctuation_count'] = df['content'].apply(
        lambda t: len(re.findall(r'[!?]', t))
    )
    return df


def process_reviews(product_url: str) -> pd.DataFrame:
    df = _fetch_reviews(product_url)
    df = _engineer(df)

    scores = []
    for _, row in df.iterrows():
        cls_emb = _encode(row['content'])
        engineered = torch.tensor(
            [[row['length'], row['uppercase_ratio'],
              row['keyword_flag'], row['punctuation_count']]],
            dtype=torch.float32
        )
        raw_score = _scorer(cls_emb, engineered)
        calibrated = torch.clamp((raw_score - 4.5) * 15, 0, 100).item()
        scores.append(calibrated)

    df['likelihood'] = scores
    df['flagged'] = df['likelihood'] >= 70
    return df

