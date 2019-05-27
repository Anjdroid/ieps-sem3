import os
from bs4 import BeautifulSoup
import codecs
import operator
import time


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


if __name__ == "__main__":
    start_time = time.time()

    query = "predelovalne dejavnosti"
    # query = "trgovina"
    # query = "social services"

    query_list = (query.lower()).split(" ")
    freq = {}

    for r, d, f in os.walk("../data/"):
        for file in f:
            if ".html" in file:
                content = (get_html_content(r, file)).lower()
                counter = 0
                for x in query_list:
                    counter = counter + content.count(x)

                if counter > 0:
                    freq[r + "/" + file] = counter

    sorted_freq = sorted(freq.items(), key=operator.itemgetter(1), reverse=True)

    print("Results for a query: \"" + query + "\" ")
    print("")

    elapsed_time = time.time() - start_time
    print("Results found in " + str(elapsed_time) + "s.")
    print("")

    print("Frequencies Document                                  Snippet")
    print("----------- ----------------------------------------- -----------------------------------------------------------")
    for key, value in sorted_freq:
        path = key[:-(len(str((key.split("/"))[-1])) + 1)]
        filename = (key.split("/"))[-1]
        print(str(value), end="")
        for i in range(len("----------- ") - len(str(value))):
            print(" ", end="")
        print(filename, end="")
        for i in range(len("----------------------------------------- ") - len(str(filename))):
            print(" ", end="")
        content = get_html_content(path, filename)
        content_list = content.split("\n")

        stevec = 0
        snippet = ""
        for cl in content_list:
            content_list_list = cl.split(" ")
            used_words = []
            last_word = 0
            for ql in range(len(query_list)):
                for cll in range(len(content_list_list)):
                    if query_list[ql] in (content_list_list[cll]).lower() and cll not in used_words and stevec < 5:
                        stevec = stevec + 1
                        if cll - 3 == 0:
                            snippet = snippet + content_list_list[cll - 3] + " " + content_list_list[cll - 2] + " " + \
                                      content_list_list[cll - 1] + " "
                        elif cll - 3 > 0:
                            if len(snippet) >= 4 and "... " == snippet[(len(snippet) - 4) : len(snippet)]:
                                snippet = snippet + content_list_list[cll - 3] + " " + content_list_list[
                                    cll - 2] + " " + content_list_list[cll - 1] + " "
                            else:
                                snippet = snippet + "... " + content_list_list[cll - 3] + " " + content_list_list[
                                    cll - 2] + " " + content_list_list[cll - 1] + " "
                        elif cll - 2 == 0:
                            snippet = snippet + content_list_list[cll - 2] + " " + content_list_list[cll - 1] + " "
                        elif cll - 1 == 0:
                            snippet = snippet +content_list_list[cll - 1] + " "
                        snippet = snippet + content_list_list[cll] + " "
                        used_words.append(cll)
                        last_word = cll
                        if ql + 1 < len(query_list) and cll + 1 < len(content_list_list) and query_list[ql + 1] in (
                                content_list_list[cll + 1]).lower() and cll + 1 not in used_words:
                            snippet = snippet + content_list_list[cll + 1] + " "
                            used_words.append(cll + 1)
                            last_word = cll + 1
                            if ql + 2 < len(query_list) and cll + 2 < len(content_list_list) and query_list[ql + 2] in (
                                    content_list_list[cll + 2]).lower() and cll + 2 not in used_words:
                                snippet = snippet + content_list_list[cll + 2] + " "
                                used_words.append(cll + 2)
                                last_word = cll + 2
                                if ql + 3 < len(query_list) and cll + 3 < len(content_list_list) and query_list[
                                    ql + 3] in (content_list_list[cll + 3]).lower() and cll + 3 not in used_words:
                                    snippet = snippet + content_list_list[cll + 3] + " "
                                    used_words.append(cll + 3)
                                    last_word = cll + 3
                                    if ql + 4 < len(query_list) and cll + 4 < len(content_list_list) and query_list[
                                        ql + 4] in (content_list_list[cll + 4]).lower() and cll + 4 not in used_words:
                                        snippet = snippet + content_list_list[cll + 4] + " "
                                        used_words.append(cll + 4)
                                        last_word = cll + 4
                        if last_word + 1 == len(content_list_list) - 1:
                            snippet = snippet + content_list_list[last_word + 1] + " "
                        elif last_word + 2 == len(content_list_list) - 1:
                            snippet = snippet + content_list_list[last_word + 1] + " " + content_list_list[
                                last_word + 2] + " "
                        elif last_word + 3 == len(content_list_list) - 1:
                            snippet = snippet + content_list_list[last_word + 1] + " " + content_list_list[
                                last_word + 2] + " " + content_list_list[last_word + 3] + " "
                        elif last_word + 3 < len(content_list_list) - 1:
                            snippet = snippet + content_list_list[last_word + 1] + " " + content_list_list[
                                last_word + 2] + " " + content_list_list[last_word + 3] + " ... "

        print(snippet)
