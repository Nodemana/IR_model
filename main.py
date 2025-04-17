from parser import Rev1_Parser, Q_Parser

def main():
    Rev1_Coll = Rev1_Parser("common-english-words.txt", "RCV1v2")

    for news_dict in Rev1_Coll.newscollectiondict.values():
        print(news_dict["news_item"].newsID)
        if len(news_dict["tf_idf"]) > 30:
            print(news_dict["tf_idf"][:30])
        else:
            print(news_dict["tf_idf"])

    #  print(Rev1_Coll)

main()
"""
def load_stopwords(stop_word_path):
    words = []
    if(stop_word_path[-3:] == "txt"):
        contents = load_file(stop_word_path)
        for content in contents:
            words += content.split(",")
    else:
        print("Stop words not a text file.")
        return None
    return words

def load_file(file_path):
    file = open(file_path)
    content = file.readlines()
    return content

stop_words = load_stopwords("common-english-words.txt")
query = "FRANCE: Reuters French Advertising & Media Digest - Aug 6"
print(Q_Parser(query, stop_words))
"""
