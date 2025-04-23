from Parser import Rev1_Parser, Q_Collection
from Q_Parser import Q_Parser


def main():
    # TASK 1.3
    Q1_queries = ["FRANCE: Reuters French Advertising & Media Digest - Aug 6", "UK: Britain's Channel 5 to broadcast Fashion Awards.", "ISRAEL: Shooting, protests spread in Gaza, West Bank"]
    for query in Q1_queries:
            query_tf = Q_Parser(query, "common-english-words.txt")
            print(query_tf)

    Rev1_Coll = Rev1_Parser("common-english-words.txt", "RCV1v2")
    for news_dict in Rev1_Coll.newscollectiondict.values():

        print(f"\n{news_dict["news_item"]}")
        for term in news_dict["news_item"].ordered_terms:
            print(f"{term} : {news_dict["news_item"].ordered_terms[term]}")


    # TASK 2.1
    print(f"There are {len(Rev1_Coll.newscollectiondict)} documents in this data set and contains {Rev1_Coll.df.total()} terms\n")
    print("The following are the terms' document-frequency:")
    for term in dict(sorted(Rev1_Coll.df.items(), key=lambda item: item[1], reverse=True)).keys():
        print(f"{term} : {Rev1_Coll.df[term]}")

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

        Q2_queries = ["FRANCE: Reuters French Advertising & Media Digest - Aug 6", "UK: Britain's Channel 5 to broadcast Fashion Awards.", "ISRAEL: Shooting, protests spread in Gaza, West Bank"]

        for query in Q2_queries:
            scores = Q_Collection(query, Rev1_Coll, "common-english-words.txt")
            f.write(f"The Ranking Result for query: {query}\n\n")
            for doc in scores.keys():
                f.write(f"{doc} : {scores[doc]}\n")
            f.write("\n")

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
    #  print(Rev1_Coll)

main()


