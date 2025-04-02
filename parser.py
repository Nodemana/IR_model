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

        # Clean the content by removing HTML entities and digits
        text = re.sub(r"&quot;", "", text)  # Remove &quot;
        text = re.sub(r"\d+", "", text)    # Remove all numbers

        # Define separators (characters that split the words)
        separators = r"[,\.\-\:\&\s\(\)\!\*]"
        words = re.split(separators, text)

        # Filter out stop words
        words = [word.strip().lower() for word in words if word.strip().lower() not in stopping_words]

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

