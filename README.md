# TruthLens: A Scalable AI System for Detecting Fake Reviews and Counterfeit Products




## Overview

TruthLens is an open-source, AI-powered pipeline that enables independent detection of deceptive product reviews and counterfeit listings on major e-commerce marketplaces. In an ecosystem overwhelmed by manipulation and restricted data access, TruthLens delivers reproducible, auditable, and technically rigorous review authenticity scoring.

## Demo
https://github.com/user-attachments/assets/5cc2b815-f20d-4735-a6a2-04e021e7a97d

## Motivation

**The Growing Threat:**

* Fake reviews distort consumer perception of product quality.
* Counterfeit sellers exploit established platforms to mislead buyers.
* Platforms restrict independent scraping and block APIs, preventing third-party validation.
* Tools like Fakespot have been shut down, leaving a gap in consumer trust infrastructure.

**Why TruthLens Matters:**

* Protects consumers from fraudulent purchasing decisions.
* Supports honest sellers by neutralizing unfair competition.
* Restores transparency through open-source, explainable scoring logic.

## Core Features

* **Session-Authenticated Web Scraping:** ProWebScraper integration allows dynamic HTML extraction even behind sign-in barriers.
* **Transformer-Based Semantic Analysis:** Fine-tuned RoBERTa encoder captures contextual signals of deception.
* **Hybrid Feature Engineering:** Combines deep language embeddings with explicit anomaly detectors.
* **Composite Trust Metrics:** Each review is scored on a 0–100 fake-likelihood scale. Product-level fake ratios translate to human-readable trust grades (A–F).
* **UI:** Accessible via a web dashboard.

## Technical Architecture

### 1. Data Acquisition Layer

* **Scraper:** ProWebScraper configured with dynamic selectors and authenticated cookies.
* **Storage:** Cloud-based JSON/CSV archival of raw reviews, metadata, and page snapshots.

### 2. Preprocessing Layer

* **Text Normalization:** HTML removal, lowercasing, punctuation stripping.
* **Tokenization:** RoBERTa tokenizer → subword units → input IDs.

### 3. Inference Layer

* **Embedding Generation:** Pre-trained RoBERTa-base encoder outputs 768-dimensional \[CLS] token embeddings.
* **Feature Fusion:** Engineered heuristics include:

  * Sentiment polarity vs. star rating residuals
  * Overuse of hyperbolic/templated keywords ("best ever", "must buy")
  * N-gram overlap for repetition detection
  * Length-based anomaly detection
* **Regression Head:** MLP maps combined embedding + heuristics vector to a scalar fake-likelihood score.

### 4. Scoring & Decision Logic

* **Thresholding:** Reviews scoring ≥70 flagged as likely deceptive.
* **Aggregation:** Product-level fake ratio calculated as percentage of flagged reviews.
* **Trust Grade Mapping:**

  * A: 0–10% fake
  * B: 11–20% fake
  * C: 21–30% fake
  * D: 31–50% fake
  * F: >50% fake
* **Adjusted Rating:** Product star rating recalibrated to exclude flagged reviews.

## Dataset

**Source:** Amazon Review Authenticity Dataset (2023 edition) merged with YelpChi-style fake review annotations.

* 200,000+ reviews across multiple product verticals
* Binary labels: genuine vs. deceptive
* Balanced class distribution (\~50% fake)
* Includes metadata: star rating, verified purchase flag, review length, author ID

## Key Contributions

* Custom fine-tuning of RoBERTa for marketplace-specific language cues.
* Statistical anomaly detection fused with transformer embeddings.
* Fully transparent scoring logic with published thresholds.
* Modular PyTorch pipeline for reproducibility and research extensibility.

## Challenges & Solutions

| Challenge               | Resolution                                                                                                  |
| ----------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Data Restrictions**   | Integrated ProWebScraper with authenticated sessions to bypass blocked endpoints.                           |
| **Label Scarcity**      | Merged multiple datasets and manually relabeled samples for balance.                                        |
| **Inference Latency**   | Applied batch tokenization and mixed-precision inference to reduce batch time from \~60s to \~18s.          |
| **Browser Integration** | Developed an asynchronous Chrome content script to inject overlays post page-load with minimal CORS issues. |

## Road Ahead

**Near Term:**

* Google Chrome Extension
* Distill or quantize RoBERTa for faster inference (target: \~15s batch).
* Extend multimodal analysis: image similarity, Q\&A text consistency.
* Expand to non-English and multi-marketplace datasets.

**Long Term:**

* Establish open governance for model retraining.
* Foster community contributions to expand dataset coverage.
* Release API/SDK for independent seller integration.

## Societal Impact

* **Open Source:** Researchers can audit, reproduce, and improve the scoring pipeline.
* **Consumer Protection:** Shoppers gain verified insights before purchasing.
* **Fair Marketplace:** Sellers with authentic reviews gain trust and conversions.

## Contributing

We welcome contributions for:

* Model fine-tuning improvements
* Additional language and domain coverage
* Dataset expansions
* Front-end and extension feature enhancements

## License

TruthLens is released under the MIT License.

## Contact

For contributions, issues, or collaboration:

* **Project Lead:** Arnabi Dutta
* **Track:** A
* **Cohort:** 2

**Let’s build transparent e-commerce together.**
