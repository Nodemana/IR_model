from collections import Counter
from XMLElement import XMLCollection, XMLElement
import os
import re
import Stemmer
import math

class NewsItem():

    def __init__(self, xml_collection, stop_words, stemmer):
        self.word_total = 0
        self.terms = Counter()
        self.newsID = ""
        self.xml_collection = xml_collection  # Store for debugging
        self.stop_words = set(stop_words)

        # Process all elements in the tree structure
        for element in xml_collection.elements:
            if(element.tag == "newsitem"):
                self.newsID = element.properties.get("itemid", "")

            # Process only the pure text content of this element (not including children)
            if element.content:
                element_bag = self.bag_of_words(element.content, stemmer)
                self.terms += element_bag
        self.ordered_terms = dict(self.terms.most_common())
        self.item_size = self.terms.total()


    def clean_content(self, text, stopping_words):
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

        self.word_total += len(words)
        # Filter out stop words
        words = [word.strip().lower() for word in words if word.strip().lower() not in stopping_words and len(word) > 1]

        return words

    def stem_words(self, words, stemmer):
        return stemmer.stemWords(words)


    def bag_of_words(self, text, stemmer):
        if not text:
            return Counter()
        words = self.clean_content(text, self.stop_words)
        stems = self.stem_words(words, stemmer)
        bag = Counter()
        for stem in stems:
            stem = stem.strip()
            if stem:  # Only count non-empty words
                bag[stem] += 1
        return bag

    def __str__(self):
        output = []
        output.append("Document " + str(self.newsID) + " contains " + str(self.item_size) + " and has a total " + str(self.word_total) + " words.")
        for key, value in self.ordered_terms.items():
            output.append(str(key) + ": " + str(value))
        return "\n".join(output)

class NewsCollection():

    def __init__(self, data_dir, stop_word_path, stemmer):

        self.files = self.load_dir(data_dir)
        self.stopwordList = self.load_stopwords(stop_word_path)
        self.stemmer = stemmer
        self.newscollectiondict = self.generate_newscollection(self.files, self.stopwordList)
        self.ndocs = len(self.newscollectiondict)
        self.df = self.my_df() # Uses 1 + log(raw_term_count)

        self.test = self.newscollectiondict["783803"]["news_item"]
        print(self.test.newsID)
        self.tf_idf = self.my_tfidf(self.test.terms, self.df, self.ndocs)
        self.all_tfidf()

    def generate_newscollection(self, file_contents, stopwordList):
        news_collection = {}
        for content in file_contents:
            xml_collection = XMLCollection(content)
            news_item = NewsItem(xml_collection, stopwordList, self.stemmer)
            news_collection[news_item.newsID] = {"news_item": news_item, "tf_idf": None}
        return news_collection

    def load_dir(self, dir_path):
        files_content = []
        for file in os.scandir(dir_path):
            if file.is_file():
                files_content.append(self.load_file(file.path))
        return files_content

    def load_stopwords(self, stop_word_path):
        words = []
        if(stop_word_path[-3:] == "txt"):
            contents = self.load_file(stop_word_path)
            for content in contents:
                words += content.split(",")
        else:
            print("Stop words not a text file.")
            return None
        return words

    def load_file(self, file_path):
        file = open(file_path)
        content = file.readlines()
        return content

    def my_df(self):
        #raw_count = Counter()
        df = Counter()

        for news_dict in self.newscollectiondict.values():
            for term in news_dict["news_item"].terms.keys():
              # raw_count[term] += item.terms[term]
               df[term] += 1
        #tf = {}
        #for term in raw_count:
        #    tf[term] = 1 + math.log(raw_count[term])

        return df #, tf

    # This is redundant, idf is also calculated in my_tfidf
    def my_idf(self, df):
        idf = {}

        for term in df:
            idf[term] = math.log(self.ndocs / df[term])
        #print(idf)
        return idf

    def my_tfidf(self, doc, d_f, ndocs):
        """
        Compute the normalized TF·IDF weights for one document.

        Args:
          doc    – either a dict {term: freq, …} or a NewsItem with .terms Counter
          d_f    – dict {term: document_frequency, …}
          ndocs  – total number of documents in the collection

        Returns:
          A dict {term: tfidf_weight, …} for all terms in `doc`.
        """
        # 1) pull out the raw term frequencies
        if hasattr(doc, 'terms'):
            freqs = doc.terms
        else:
            freqs = doc

        # 2) build IDF for each term in the vocabulary (Eq. (1)): idf_t = log(N / df_t)
        idf = {t: math.log(ndocs / d_f[t]) for t in d_f}

        # 3) compute log‐normalized TF for this doc: tf_t = 1 + log(freq_t)  (if freq_t > 0)
        tf = {t: 1 + math.log(f) for t, f in freqs.items() if f > 0}

        # 4) un‐normalized TF·IDF
        raw_tfidf = {t: tf[t] * idf[t] for t in tf if t in idf}

        # 5) L₂‐normalize:  ‖v‖₂ = sqrt(∑_k v_k²)
        norm = math.sqrt(sum(v*v for v in raw_tfidf.values()))
        if norm > 0:
            for t in raw_tfidf:
                raw_tfidf[t] /= norm

        # 6) sort descending by weight and return as an ordered list
        sorted_dict = dict(sorted(raw_tfidf.items(),
                         key=lambda item: item[1],
                         reverse=True))
        return sorted_dict

    # Computes tf_idf for all news items in collection
    def all_tfidf(self):
        for news_dict in self.newscollectiondict.values():
            news_dict["tf_idf"] = self.my_tfidf(news_dict["news_item"], self.df, self.ndocs)

    def rank_tfidf(self, q_tfidf):
        scores = {}
        for newsID in self.newscollectiondict.keys():
            scores[newsID] = 0
            for term in q_tfidf.keys():
                #print(self.newscollectiondict[newsID]["tf_idf"])
                if term in self.newscollectiondict[newsID]["tf_idf"]:
                    scores[newsID] += q_tfidf[term] * self.newscollectiondict[newsID]["tf_idf"][term]

        return dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))



    def __str__(self):
        output = []
        for item in self.newscollectiondict.values():
            output.append(str(item["news_item"]))
        return "\n".join(output)

"""
stemmer = Stemmer.Stemmer('english')
newscollection = NewsCollection("RCV1v2", "common-english-words.txt", stemmer)

# Uncomment to debug the element tree structure
#if newscollection.newscollectionlist:
#    first_item = newscollection.newscollectionlist[0]
#    print("Debugging first news item structure:")
#    #for root_element in first_item.xml_collection.root_elements:
#     #   first_item.debug_print_element_tree(root_element)
#    print(first_item.newsID)
#    print(first_item.terms)

if newscollection.newscollectionlist:
    for newsitem in newscollection.newscollectionlist:
        if newsitem.newsID == "783803":
            print(newsitem.newsID)
            print(newsitem.terms)
"""
