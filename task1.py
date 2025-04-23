from Parser import Rev1_Parser
from Q_Parser import Q_Parser


def main():
    #TASK 1.1
    """
    Words have been defined as space seperated character strings which exist
    within the document after special characters, numbers, punctuation and
    web links have been removed. But before stop words have been removed.

    Terms are the stemmed remaining words after stop words have been removed.
    This has been done with the porter

    """

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





