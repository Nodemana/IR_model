from src.Parser import Rev1_Parser, Q_Collection

def main():

    """
    Task 2 requires ranking documents based on queries derived from document
    titles using a relatively simple ranking algorithm that computes the dot
    product between the TF-IDF weights of the query terms and those of the
    documents. Normally, using the dot product for ranking introduces a bias
    toward longer documents or queries, as they tend to have higher vector
    magnitudes and thus larger raw scores. Cosine similarity addresses this
    issue by normalising the dot product by the magnitudes of both the query
    and document vectors, effectively neutralising biases related to document
    and query length.

    However, in this task, both the query and document TF-IDF vectors are
    already L2-normalised before ranking, meaning each vector has unit length.
    As a result, the magnitudes of the vectors are all equal to one, making the
    dot product mathematically equivalent to cosine similarity. Consequently,
    there is NO FUNCTIONAL DIFFERENCE between using the dot product or cosine
    similarity for ranking in this case, since normalisation has already
    removed length bias and ensures that the scores reflect the angle between
    vectors rather than their magnitudes. Dot product actually becomes the
    better choice due to it being computationally effiient vs cosine similarity.

    """

    Rev1_Coll = Rev1_Parser("common-english-words.txt", "RCV1v2")

    # TASK 2.1
    # It was not clear in the specification if this should be added to the text file or not, so I just left it as print statements.
    print(f"There are {len(Rev1_Coll.newscollectiondict)} documents in this data set and contains {Rev1_Coll.df.total()} terms\n")
    print("The following are the terms' document-frequency:")
    for term in dict(sorted(Rev1_Coll.df.items(), key=lambda item: item[1], reverse=True)).keys():
        print(f"{term} : {Rev1_Coll.df[term]}")

    # TASK 2.2
    # Please see my_tfidf in NewsCollection class in src/NewsItem.py

    # TASK 2.3
    with open("ZachEdwards_Q2.txt", "w", encoding="utf-8") as f:

        for news_dict in Rev1_Coll.newscollectiondict.values():
            f.write(f"Document {news_dict["news_item"].newsID} contains {news_dict["news_item"].get_size()} terms\n")
            if len(news_dict["tf_idf"]) > 30:
                i = 0
                for term in news_dict["tf_idf"]:
                    if i == 30:
                        break
                    f.write(f"{term} : {news_dict["tf_idf"][term]}\n")
                    i += 1
            else:
                for term in news_dict["tf_idf"]:
                    f.write(f"{term} : {news_dict["tf_idf"][term]}\n")

            f.write("\n")

        Q2_queries = ["FRANCE: Reuters French Advertising & Media Digest - Aug 6", "UK: Britain's Channel 5 to broadcast Fashion Awards.", "ISRAEL: Shooting, protests spread in Gaza, West Bank", "ISRAEL: Death toll 33 Arabs, 10 Israelis at 1400 gmt."]

        for query in Q2_queries:
            scores = Q_Collection(query, Rev1_Coll, "common-english-words.txt")
            f.write(f"The Ranking Result for query: {query}\n\n")
            for doc in scores.keys():
                f.write(f"{doc} : {scores[doc]}\n")
            f.write("\n")

main()

