import re
from collections import Counter
import Stemmer
from NewsItem import NewsCollection


def Rev1_Parser(stop_words, inputfolder):
    stemmer = Stemmer.Stemmer('english')
    Rev1_Coll = NewsCollection(inputfolder, stop_words, stemmer)
    return Rev1_Coll

def Q_Parser(query, stop_words):

    # At the moment website URLs are not removed.
    def clean_content(text, stopping_words):
        if not text:
            return text
        # Remove web links
        text = re.sub(r'https?://\S+', '', text)

        # Remove (c) symbols (case-insensitive)
        text = re.sub(r'\(c\)', '', text, flags=re.IGNORECASE)

        # Remove apostrophe-s (e.g., "John's" becomes "John")
        text = re.sub(r"\'s\b", '', text)

        # Remove plus signs or other unwanted symbols (you can add more if needed)
        text = re.sub(r'\+', '', text)
        # Clean the content by removing HTML entities and digits
        text = re.sub(r"&quot;", "", text)  # Remove &quot;
        text = re.sub(r"\d+", "", text)    # Remove all numbers

        # Remove punctuation by replacing non-word and non-space characters with a space
        text = re.sub(r'[^\w\s]', ' ', text)

        # Define separators (characters that split the words)
        words = re.split(r"\s+", text)


        # Filter out stop words
        words = [word.strip().lower() for word in words if word.strip().lower() not in stopping_words and len(word) > 1]

        return words

    def stem_words(words, stemmer):
        return stemmer.stemWords(words)


    def bag_of_words(text, stemmer, stop_words):
        if not text:
            return Counter()
        words = clean_content(text, stop_words)
        stems = stem_words(words, stemmer)
        bag = Counter()
        for stem in stems:
            stem = stem.strip()
            if stem:  # Only count non-empty words
                bag[stem] += 1
        return bag

    stemmer = Stemmer.Stemmer('english')

    return bag_of_words(query, stemmer, stop_words)

def Q_Collection(query, collection, stop_words):
    query_tf = Q_Parser(query, stop_words)
    query_idf = collection.my_tfidf(query_tf, collection.df, collection.ndocs)

    scores = collection.rank_tfidf(query_idf)
    return scores


