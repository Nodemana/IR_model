from Parser import Rev1_Parser

def main():
    Rev1_Coll = Rev1_Parser("common-english-words.txt", "RCV1v2")

    #TASK 3.3
    Q3_queries = ["The British-Fashion Awards", "Rocket attacks", "FRANCE: Reuters French Advertising & Media Digest - Aug 6", "US EPA ranks Geo Metro car most fuel-efficient 1997 car."]
    with open("ZachEdwards_Q3.txt", "w", encoding="utf-8") as f:
        f.write(f"Average document length for this collection is: {Rev1_Coll.avg_length()}\n")
        for query in Q3_queries:

            f.write(f"The query is: {query}\n\n")
            bm25_scores = Rev1_Coll.my_bm25(query, Rev1_Coll.df)
            top_6 = dict(list(bm25_scores.items())[:6])

            f.write("The following are the BM25 score for each document:\n")
            for doc in bm25_scores.keys():
                f.write(f"Document ID: {doc}, Doc Length: {Rev1_Coll.newscollectiondict[doc]["news_item"].get_size()} -- BM25 Score: {bm25_scores[doc]}\n")
            f.write("\n")

            f.write(f"For query \"{query}\", the top-6 relevant documents are:\n")
            for doc in top_6.keys():
                f.write(f"{doc} {top_6[doc]}\n")
            f.write("\n")


main()

