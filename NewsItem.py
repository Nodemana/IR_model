from collections import Counter
from XMLElement import XMLCollection, XMLElement
import os
import re
import Stemmer

from load_xml import load_file



class NewsItem():

    def __init__(self, xml_collection, stop_words, stemmer):
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

        self.item_size = self.terms.total()


    def clean_content(self, text, stopping_words):
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

    def process_element_tree(self, element, stop_words):
        """Process an element and all its children recursively"""
        # Process this element's content
        if element.content:
            element_bag = self.bag_of_words(element.content)
            self.terms += element_bag

        # Process all children
        for child in element.children:
            self.process_element_tree(child, stop_words)

    def debug_print_element_tree(self, element, level=0):
        """Print the element tree structure with content for debugging"""
        indent = "  " * level
        print(f"{indent}Tag: {element.tag}")
        print(f"{indent}Properties: {element.properties}")
        print(f"{indent}Content (pure text): {element.content}")
        print(f"{indent}Children count: {len(element.children)}")

        for child in element.children:
            self.debug_print_element_tree(child, level + 1)


class NewsCollection():

    def __init__(self, data_dir, stop_word_path, stemmer):

        self.files = self.load_dir(data_dir)
        self.stopwordList = self.load_stopwords(stop_word_path)
        self.stemmer = stemmer
        self.newscollectionlist = self.generate_newscollection(self.files, self.stopwordList)


    def generate_newscollection(self, file_contents, stopwordList):
        news_collection = []
        for content in file_contents:
            xml_collection = XMLCollection(content)
            news_item = NewsItem(xml_collection, stopwordList, self.stemmer)
            news_collection.append(news_item)
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





