from nltk.sentiment.vader import SentimentIntensityAnalyzer
from transformers import pipeline

# Initialize analyzers
vader = SentimentIntensityAnalyzer()
hf_pipeline = None # Initialize to None

try:
    # Attempt to load the DistilBERT model
    hf_pipeline = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")
except Exception:
    # If the model download/initialization fails (e.g., due to memory or no internet), fall back
    print("Warning: HuggingFace pipeline failed to load. Falling back to VADER.")
    hf_pipeline = None

def classify_sentiment(text):
    """Return 'positive', 'negative', or 'neutral' for the given text."""
    if hf_pipeline:
        # Use HuggingFace DistilBERT
        # Truncate text to fit the model's max sequence length (512 tokens)
        result = hf_pipeline(text[:512])[0]
        label = result['label']
        return label.lower()
    else:
        # Fallback to VADER lexicon
        score = vader.polarity_scores(text)['compound']
        if score > 0.05:
            return 'positive'
        elif score < -0.05:
            return 'negative'
        else:
            return 'neutral'

# Example (for testing purposes only)
if __name__ == '__main__':
    texts = ["Company announces record profits", "Stock falls amid rumors", "No major news today"]
    for t in texts:
        print(t, "->", classify_sentiment(t))