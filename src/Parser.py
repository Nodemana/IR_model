import Stemmer
from .NewsItem import NewsCollection
from .Q_Parser import Q_Parser

def Rev1_Parser(stop_words, inputfolder):
    stemmer = Stemmer.Stemmer('english')
    Rev1_Coll = NewsCollection(inputfolder, stop_words, stemmer)
    return Rev1_Coll

def Q_Collection(query, collection, stop_words):
    query_tf = Q_Parser(query, stop_words)
    query_idf = collection.my_tfidf(query_tf, collection.df, collection.ndocs)

    scores = collection.rank_tfidf(query_idf)
    return scores


