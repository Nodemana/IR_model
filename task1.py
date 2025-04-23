from src.Parser import Rev1_Parser
from src.Q_Parser import Q_Parser


def main():
    #TASK 1.1
    """
    Words have been defined as space seperated character strings which exist
    within the document after special characters, numbers, punctuation and
    web links have been removed. But before stop words have been removed.

    The definition of a term is dependent on the algorithm used to determine
    them. In this specific case terms are a subset of words that group
    morphological variants (e.g jumps or jumped) under a common representation
    (e.g jump). Terms also preserve partial semantic meaning but loses
    gramatical nuance (happily preserves happy but loses -ly).
    The terms in this project were produced by first removing words which lack
    standalone semantic meaning such as "the" or "of". Then the porter2 stemming
    algorithm was applied to the remaining words to create a list of terms which
    abide by the definition defined above.

    The stop words used can be seen in "common-english-words.txt".
    Added stop words were:
    reuters, couldn, wouldn, shouldn

    reuters is in every document as each document is a Reuters news artical,
    which means that this word adds no meaning and can be removed.

    "could, wouldn and shouldn" were removed as after the apostraphes are
    removed and replaced with spaces these terms are left and provide little
    to no meaning.

    """

    #TASK 1.2
    # Please see Q_Parser function in src/Q_Parser.py

    # TASK 1.3
    Q1_queries = ["FRANCE: Reuters French Advertising & Media Digest - Aug 6", "UK: Britain's Channel 5 to broadcast Fashion Awards.", "ISRAEL: Shooting, protests spread in Gaza, West Bank"]
    Rev1_Coll = Rev1_Parser("common-english-words.txt", "RCV1v2")

    with open("ZachEdwards_Q1.txt", "w", encoding="utf-8") as f:
        f.write(str(Rev1_Coll))

        for query in Q1_queries:
            query_tf = Q_Parser(query, "common-english-words.txt")
            f.write(f"Query: {query}\n")
            f.write("The parsed query:\n")
            f.write(f"{str(query_tf)}\n\n")


main()





