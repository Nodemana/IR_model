import Stemmer
from .NewsItem import NewsCollection
from .Q_Parser import Q_Parser


def Rev1_Parser(stop_words, inputfolder):
    """
    Initialise a NewsCollection from raw documents.

    Parameters:
        stop_words (str): Filename of comma seperated words to exclude during tokenization.
        inputfolder (str): Filesystem path containing news article files.

    Returns:
        NewsCollection: An object representing the parsed and preprocessed corpus.
    """
    # Set up an English stemmer for term normalization
    stemmer = Stemmer.Stemmer('english')
    # Build the collection, applying stop word filtering and stemming
    Rev1_Coll = NewsCollection(inputfolder, stop_words, stemmer)
    return Rev1_Coll


def Q_Collection(query, collection, stop_words):
    """
    Rank documents in a NewsCollection according to a search query.

    This function parses the input query into term frequencies,
    weights them by collection-level IDF, and returns documents
    sorted by their TF-IDF relevance scores.

    Parameters:
        query (str): The raw search string.
        collection (NewsCollection): The corpus to search.
        stop_words (iterable of str): Filename of comma seperated words to exclude during tokenization.

    Returns:
       sorted dict: Ranked list of (document_id, score) pairs.
    """
    # Convert query text into term-frequency mapping
    query_tf = Q_Parser(query, stop_words)
    # Weight by inverse document frequency
    query_idf = collection.my_tfidf(query_tf, collection.df, collection.ndocs)

    # Score and rank each document by TF-IDF similarity
    scores = collection.rank_tfidf(query_idf)
    return scores

