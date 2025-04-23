from collections import Counter
from .XMLElement import XMLCollection
from .Q_Parser import Q_Parser

import os
import re
import math

class NewsItem():
    """
    Wraps a single news item, extracting and counting normalized, stemmed terms.
    """

    def __init__(self, xml_collection, stop_words, stemmer):
        """
        Initialize the NewsItem:
        - Parse XML elements to extract text
        - Clean, tokenize, remove stop-words, stem, and count terms
        - Track total word count and document ID
        """
        self.terms = Counter()
        self.item_size = 0
        self.newsID = ""
        self.stop_words = set(stop_words)
        print(self.stop_words)
        # Process each element in the XML tree
        for element in xml_collection.elements:
            if element.tag == "newsitem":
                self.newsID = element.properties.get("itemid", "")
            if element.content:
                element_bag = self.bag_of_words(element.content, stemmer)
                self.terms += element_bag
        self.ordered_terms = dict(self.terms.most_common())

    def clean_content(self, text, stopping_words):
        """
        Normalize raw text:
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
        self.set_size(self.get_size() + len(words))

        # strip, lowercase, filter stop-words and single characters
        words = [word.strip().lower() for word in words if word.strip().lower() not in stopping_words and len(word) > 1]

        return words

    def stem_words(self, words, stemmer):
        """
        Apply the provided stemmer to each token.
        Returns a list of stemmed tokens.
        """
        return stemmer.stemWords(words)

    def bag_of_words(self, text, stemmer):
        """
        Convert raw text into a term-frequency Counter:
        1. Clean content
        2. Stem words
        3. Count non-empty stems
        """
        if not text:
            return Counter()
        words = self.clean_content(text, self.stop_words)
        stems = self.stem_words(words, stemmer)
        bag = Counter()
        for stem in stems:
            s = stem.strip()
            if s:
                bag[s] += 1
        return bag

    def add_term(self, term_bag):
        """
        Merge another Counter of term frequencies into this item.
        """
        self.terms += term_bag
        self.ordered_terms = dict(self.terms.most_common())

    def get_size(self):
        """
        Return the total number of raw words processed.
        """
        return self.item_size or 0

    def set_size(self, size):
        """
        Update the document's word count.
        """
        self.item_size = size

    def __str__(self):
        """
        String representation: header line + each term:freq on its own line.
        """
        lines = [
            f"Document {self.newsID} contains {sum(self.terms.values())} indexing terms"
            f" and has a total {self.get_size()} words."
        ]
        for term, freq in self.ordered_terms.items():
            lines.append(f"{term}: {freq}")
        return "\n".join(lines) + "\n"

class NewsCollection():
    """
    Holds a collection of NewsItem objects and computes global statistics
    like document frequencies, TF-IDF, and BM25 rankings.
    """

    def __init__(self, data_dir, stop_word_path, stemmer):
        """
        Load XML files, parse stop-words, create NewsItem for each document,
        compute document-frequency (df), TF-IDF vectors, and prepare for BM25.
        """
        self.files = self.load_dir(data_dir)
        self.stopwordList = self.load_stopwords(stop_word_path)
        self.stemmer = stemmer
        self.totalDocLength = 0
        self.newscollectiondict = self.generate_newscollection(self.files, self.stopwordList)
        self.ndocs = len(self.newscollectiondict)
        self.df = self.my_df()
        self.all_tfidf()

    def generate_newscollection(self, file_contents, stopwordList):
        """
        Instantiate NewsItem for each file's XML content.
        Track total word count across documents.
        Returns a dict of {newsID: {"news_item": NewsItem, "tf_idf": None}}.
        """
        news_collection = {}
        for content in file_contents:
            xml_collection = XMLCollection(content)
            news_item = NewsItem(xml_collection, stopwordList, self.stemmer)
            news_collection[news_item.newsID] = {"news_item": news_item, "tf_idf": None}
            self.totalDocLength += news_item.get_size()
        return news_collection

    def load_dir(self, dir_path):
        """
        Read all files in a directory and return list of their line lists.
        """
        contents = []
        for entry in os.scandir(dir_path):
            if entry.is_file():
                contents.append(self.load_file(entry.path))
        return contents

    def load_stopwords(self, stop_word_path):
        """
        Load comma-separated stop-words from a .txt file.
        """
        if stop_word_path.endswith(".txt"):
            content = self.load_file(stop_word_path)
            return [w for line in content for w in line.split(",")]
        else:
            raise ValueError("Stop words file must be a .txt")

    def load_file(self, file_path):
        """
        Read all lines from a file and return as a list of strings.
        """
        with open(file_path, encoding='utf-8') as f:
            return f.readlines()

    def my_df(self):
        """
        Compute document frequency: for each term, count how many docs contain it.
        Returns a Counter {term: df}.
        """
        df = Counter()
        for nd in self.newscollectiondict.values():
            for term in nd["news_item"].terms:
                df[term] += 1
        return df

    def my_tfidf(self, doc, d_f, ndocs):
        """
        Compute L2-normalized TF-IDF for a single document.
        Args:
          doc   - NewsItem or dict(term: freq)
          d_f   - document frequencies
          ndocs - total number of documents
        Returns a dict of normalised tf-idf weights sorted descending.
        """
        freqs = doc.terms if hasattr(doc, 'terms') else doc
        idf = {t: math.log10(ndocs / d_f[t]) for t in d_f} # Compute IDF
        tf = {t: 1 + math.log10(f) for t, f in freqs.items() if f > 0} # Compute TF
        raw = {t: tf[t] * idf[t] for t in tf if t in idf} # Compute TF*IDF Numerator
        norm = math.sqrt(sum(v*v for v in raw.values())) # Compute Normalisation
        if norm > 0:
            for t in raw:
                raw[t] /= norm # Apply Normalisation for each Term
        return dict(sorted(raw.items(), key=lambda kv: kv[1], reverse=True))

    def all_tfidf(self):
        """
        Compute and store tf-idf vectors for every NewsItem in the collection.
        """
        # nd stands for news dictionary {"news_item" : NewsItem, "tf_idf": TF*IDF}
        for nd in self.newscollectiondict.values():
            nd["tf_idf"] = self.my_tfidf(nd["news_item"], self.df, self.ndocs)

    def rank_tfidf(self, q_tfidf):
        """
        Score each document by abstract ranking model (dot product) to the query tf-idf vector.
        Returns a dict of {newsID: score} sorted descending.
        """
        # nid stands for newsID and nd is same as above
        scores = {nid: 0 for nid in self.newscollectiondict}
        for nid, nd in self.newscollectiondict.items():
            for term, weight in q_tfidf.items():
                scores[nid] += weight * nd["tf_idf"].get(term, 0)
        return dict(sorted(scores.items(), key=lambda kv: kv[1], reverse=True))

    def avg_length(self):
        """
        Compute average document length (in raw words) across the collection.
        """
        return self.totalDocLength / self.ndocs if self.ndocs else 0

    def my_bm25(self, q, df):
        """
        Compute BM25 scores for query q against all documents.
        Clamps negative IDF to zero.
        Returns a dict {newsID: score} sorted descending.
        """
        scores = {}
        k1, k2, b = 1.2, 100, 0.75
        query_tf = Q_Parser(q, self.stopwordList)
        for nid, nd in self.newscollectiondict.items():
            score = 0
            d = nd["news_item"]
            for term, qf in query_tf.items():
                f = d.ordered_terms.get(term, 0)
                idf = max(0, math.log10((self.ndocs - df[term] + 0.5) / (df[term] + 0.5)))
                K = k1 * ((1 - b) + b * (d.get_size() / self.avg_length()))
                score += idf * ((k1 + 1) * f) / (K + f) * ((k2 + 1) * qf) / (k2 + qf)
            scores[nid] = score
        return dict(sorted(scores.items(), key=lambda kv: kv[1], reverse=True))

    def __str__(self):
        """
        Concatenate the string representations of all NewsItems.
        """
        return "\n".join(str(nd["news_item"]) for nd in self.newscollectiondict.values())

