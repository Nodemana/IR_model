import re
import Stemmer
from collections import Counter

def Q_Parser(query, stop_words):
    """
    Produce a term-frequency Counter from query text.

    Parameters:
        query (str): Input text.
        stop_words (str or iterable): .txt path or stop-word list.

    Returns:
        Counter: Stemmed token frequencies.
    """

    def load_file(path):
        """Read lines from a file."""
        with open(path) as f: return f.readlines()

    def load_stopwords(src):
        """Load comma-separated words from .txt or use iterable."""
        if isinstance(src, str) and src.lower().endswith('.txt'):
            words = []
            for line in load_file(src):
                words.extend(w.strip() for w in line.split(',') if w.strip())
            return words
        return list(src)

    def clean_content(text, stopping_words):
        """
        Normalise raw text:
        - Remove URLs, HTML entities, digits, and unwanted symbols
        - Split into words, lowercase, strip punctuation
        - Filter out stop-words and single-character tokens
        - Update document word count
        Returns a list of cleaned word tokens.
        """
        if not text:
            return []
        text = re.sub(r'https?://\S+', '', text)
        text = re.sub(r'\(c\)', '', text, flags=re.IGNORECASE)
        text = re.sub(r"\'s\b", '', text)
        text = re.sub(r'\+', '', text)
        text = re.sub(r"&quot;", "", text)
        text = re.sub(r"\d+", "", text)
        text = re.sub(r'[^\w\s]', ' ', text)
        words = re.split(r"\s+", text)

        # strip, lowercase, filter stop-words and single characters
        words = [word.strip().lower() for word in words if word.strip().lower() not in stopping_words and len(word) > 1]

        return words

    def stem_words(words, stemmer):
        """
        Apply the provided stemmer to each token.
        Returns a list of stemmed tokens.
        """
        return stemmer.stemWords(words)

    def bag_of_words(text, stemmer, stop_words):
        """
        Convert raw text into a term-frequency Counter:
        1. Clean content
        2. Stem words
        3. Count non-empty stems
        """
        if not text:
            return Counter()
        words = clean_content(text, stop_words)
        stems = stem_words(words, stemmer)
        bag = Counter()
        for stem in stems:
            s = stem.strip()
            if s:
                bag[s] += 1
        return bag

    stemmer = Stemmer.Stemmer('english')
    stop_words = load_stopwords(stop_words)
    return bag_of_words(query, stemmer, stop_words)

