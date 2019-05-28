import os
from bs4 import BeautifulSoup
import codecs
import nltk
from nltk.corpus import stopwords
import operator
import time
import re


def get_html_content(root, name):
    html_content = codecs.open(root + "/" + name, 'r', 'utf-8')
    soup = BeautifulSoup(html_content, features="lxml")
    # remove all script and style elements
    for script in soup(["script", "style"]):
        script.extract()

    # get text
    text = soup.get_text()
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    return '\n'.join(x for x in chunks if x)


"""
def remove_stopwords(words):
    punctuation = ['.', ',', '!', '?', '-', '>', '<', ':', ';', ')', '(', '--', '–', '/', "''", '', '|', '...', '``',
                   '»', '«']
    for p in punctuation:
        words = words.replace(p, "")

    sw = set(stopwords.words('slovenian'))

    words_list = words.split(" ")
    new_word = ""
    for w in words_list:
        if w not in sw:
            new_word = new_word + " " + w

    return new_word
"""


def data_retrieval(query):
    start_time = time.time()

    new_query = query.replace(" in", "")
    query_list = (new_query.lower()).split(" ")
    freq = {}

    for r, d, f in os.walk("../data/"):
        for file in f:
            if ".html" in file:
                content = (get_html_content(r, file)).lower()
                counter = 0
                for x in query_list:
                    all_matches = re.findall(r'\b%s\b' % x, content)
                    counter = len(all_matches)

                if counter > 0:
                    freq[r + "/" + file] = counter

    sorted_freq = sorted(freq.items(), key=operator.itemgetter(1), reverse=True)

    result = ""

    for key, value in sorted_freq:
        path = key[:-(len(str((key.split("/"))[-1])) + 1)]
        filename = (key.split("/"))[-1]
        result = result + str(value)
        for i in range(len("----------- ") - len(str(value))):
            result = result + " "
        result = result + filename
        for i in range(len("----------------------------------------- ") - len(str(filename))):
            result = result + " "
        content = get_html_content(path, filename)
        content_list = content.split("\n")

        if value > 5:
            n = 5
        else:
            n = value

        stevec = 0
        for cl in content_list:
            content_list_list = cl.split(" ")
            used_words = []
            for ql in range(len(query_list)):
                for cll in range(len(content_list_list)):
                    if re.search(r'\b%s\b' % query_list[ql],
                                 (content_list_list[cll]).lower()) is not None and cll not in used_words and stevec < n:
                        stevec = stevec + 1
                        if cll - 3 == 0:
                            result = result + content_list_list[cll - 3] + " " + content_list_list[cll - 2] + " " + \
                                     content_list_list[cll - 1] + " "
                        elif cll - 3 > 0:
                            if len(result) >= 4 and "... " == result[(len(result) - 4): len(result)]:
                                result = result + content_list_list[cll - 3] + " " + content_list_list[
                                    cll - 2] + " " + content_list_list[cll - 1] + " "
                            else:
                                result = result + "... " + content_list_list[cll - 3] + " " + content_list_list[
                                    cll - 2] + " " + content_list_list[cll - 1] + " "
                        elif cll - 2 == 0:
                            result = result + content_list_list[cll - 2] + " " + content_list_list[cll - 1] + " "
                        elif cll - 1 == 0:
                            result = result + content_list_list[cll - 1] + " "
                        result = result + content_list_list[cll] + " "
                        used_words.append(cll)
                        last_word = cll
                        if ql + 1 < len(query_list) and cll + 1 < len(content_list_list) and re.search(
                                r'\b%s\b' % query_list[ql + 1],
                                (content_list_list[cll + 1]).lower()) is not None and cll + 1 not in used_words:
                            result = result + content_list_list[cll + 1] + " "
                            used_words.append(cll + 1)
                            last_word = cll + 1
                            if ql + 2 < len(query_list) and cll + 2 < len(content_list_list) and re.search(
                                    r'\b%s\b' % query_list[ql + 2],
                                    (content_list_list[cll + 2]).lower()) is not None and cll + 2 not in used_words:
                                result = result + content_list_list[cll + 2] + " "
                                used_words.append(cll + 2)
                                last_word = cll + 2
                                if ql + 3 < len(query_list) and cll + 3 < len(content_list_list) and re.search(
                                        r'\b%s\b' % query_list[ql + 3],
                                        (content_list_list[cll + 3]).lower()) is not None and cll + 3 not in used_words:
                                    result = result + content_list_list[cll + 3] + " "
                                    used_words.append(cll + 3)
                                    last_word = cll + 3
                                    if ql + 4 < len(query_list) and cll + 4 < len(content_list_list) and re.search(
                                            r'\b%s\b' % query_list[ql + 4],
                                            (content_list_list[
                                                cll + 4]).lower()) is not None and cll + 4 not in used_words:
                                        result = result + content_list_list[cll + 4] + " "
                                        used_words.append(cll + 4)
                                        last_word = cll + 4
                        if last_word + 1 == len(content_list_list) - 1:
                            result = result + content_list_list[last_word + 1] + " "
                        elif last_word + 2 == len(content_list_list) - 1:
                            result = result + content_list_list[last_word + 1] + " " + content_list_list[
                                last_word + 2] + " "
                        elif last_word + 3 == len(content_list_list) - 1:
                            result = result + content_list_list[last_word + 1] + " " + content_list_list[
                                last_word + 2] + " " + content_list_list[last_word + 3] + " "
                        elif last_word + 3 < len(content_list_list) - 1:
                            result = result + content_list_list[last_word + 1] + " " + content_list_list[
                                last_word + 2] + " " + content_list_list[last_word + 3] + " ... "

        result = result + "\n"

    print("Results for a query: \"" + query + "\"\n")

    elapsed_time = time.time() - start_time
    print("Results found in " + str(round(elapsed_time * 1000)) + "ms.\n")

    print("Frequencies Document                                  Snippet")
    print(
        "----------- ----------------------------------------- -----------------------------------------------------------")
    print(result)


if __name__ == "__main__":
    query = "predelovalne dejavnosti"
    data_retrieval(query)

    query = "trgovina"
    data_retrieval(query)

    query = "social services"
    data_retrieval(query)

    query = "statistični urad RS"
    data_retrieval(query)

    query = "otroški dodatki in državne štipendije"
    data_retrieval(query)

    query = "fakulteta"
    data_retrieval(query)
