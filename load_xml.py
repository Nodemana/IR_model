import os
import re

class XMLElement():

    def __init__(self, tag, content):
        self.tag = tag
        self.content = content


def load_file(file_path):
    file = open(file_path)
    content = file.readlines()
    return content

def get_tag_content(content):
    # Join all lines into a single string
    full_content = ''.join(content)

    # Apply regex on the full content
    pattern = r'<([^>]+)>(.*?)</\1>'
    matches = re.findall(pattern, full_content)

    # Return list of (tag, content) tuples
    return matches

def generate_elements(tuples):
    classes = []
    for tuple in tuples:
        classes.append(XMLElement(tuple[0], tuple[1]))

    return classes

def sum_words(text):
    words = text.split(" ")
    print(words)
    return len(words)

def main():
    """Example showing how to use the XML loading functions"""
    # Example XML file path
    xml_file = "741299newsML.xml"
    content = load_file(xml_file)

    #print(content)


    matches = get_tag_content(content)
    elements = generate_elements(matches)

    word_sum = 0
    for element in elements:
        if(element.tag == "p"):
            word_sum += sum_words(element.content)

    print(word_sum)



if __name__ == "__main__":
    main()

