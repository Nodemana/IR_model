from Parser import Rev1_Parser, Q_Collection

def main():
    Rev1_Coll = Rev1_Parser("common-english-words.txt", "RCV1v2")

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

main()

