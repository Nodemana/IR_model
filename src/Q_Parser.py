import re
import Stemmer
from collections import Counter

def Q_Parser(query, stop_words):

    def load_file(file_path):
        file = open(file_path)
        content = file.readlines()
        return content

    def load_stopwords(stop_word_path):
        words = []
        if(stop_word_path[-3:] == "txt"):
            contents = load_file(stop_word_path)
            for content in contents:
                words += content.split(",")
        else:
            return stop_word_path
        return words

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

    def stem_words(words, stemmer): # , stop_words):
        return stemmer.stemWords(words)
        #return [s for s in stems if s not in stop_words]


    def bag_of_words(text, stemmer, stop_words):
        if not text:
            return Counter()
        words = clean_content(text, stop_words)
        stems = stem_words(words, stemmer) #, stop_words)
        bag = Counter()
        for stem in stems:
            stem = stem.strip()
            if stem:  # Only count non-empty words
                bag[stem] += 1
        return bag

    stemmer = Stemmer.Stemmer('english')
    stop_words = load_stopwords(stop_words)
    return bag_of_words(query, stemmer, stop_words)

