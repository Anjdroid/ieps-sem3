import sqlite3
import os
from bs4 import BeautifulSoup
import codecs
import nltk
from nltk.corpus import stopwords
import time


class DataBase:
	""" Class for database operations. """
	def __init__(self, database):
		self.conn = sqlite3.connect(database)
		self.curr = self.conn.cursor()
		print("Connected to db.")

	def insert_index_word(self, text):
		self.curr.execute("INSERT OR IGNORE INTO IndexWord (word) VALUES(?);", (text,))
		print("Adding index word: ", text + "\n")
		self.commit_db()

	def insert_posting(self, w, doc, freq, idxs, word_fk):
		self.curr.execute('INSERT OR IGNORE INTO Posting (word, documentName, frequency, indexes, word) VALUES (?, ?, ?, ?, ?)', (w, doc, freq, idxs, word_fk))
		print("Adding posting: ", w + " " + doc + " " + str(freq) + " " + idxs + " " + word_fk + "\n")
		self.commit_db()

	def get_all_index_word(self):
		self.curr.execute('SELECT * FROM IndexWord')
		data = self.curr.fetchall()
		print("Data from indexWord: ", data)

	def get_all_posting(self):
		self.curr.execute('SELECT * FROM Posting')
		data = self.curr.fetchall()
		print("Data from posting: ", data)

	def get_querry_from_posting(self, word1, word2, word3, word4, word5):
		self.curr.execute('SELECT p.documentName AS docName, SUM(frequency) AS freq, GROUP_CONCAT(indexes) AS idxs FROM Posting p WHERE p.word IN (?, ?, ?, ?, ?) GROUP BY p.documentName ORDER BY freq DESC;',(word1, word2, word3, word4, word5))
		data = self.curr.fetchall()
		print("Data from querry: ", data)
		return data

	def commit_db(self):
		self.conn.commit()
		print("Data is commited.")

	def close_conn(self):
		self.conn.close()
		print("Connection to db closed.")



class FileRead:
	def __init__(self, path, data_index):
		self.path = path
		"""
			Dictionary for extracted text from html files:
			'dir_name' : {'website_name' : ['token1', 'token2', ... ]}
		"""
		self.html_content_data = {}
		self.html_tokenized_data = {}
		self.html_content = {}
		"""
		TODO:
		when running the code for the first time UNCOMMENT:
		"""
		# nltk.download('punkt')
		# nltk.download('stopwords')
		self.stopwords = self.load_stopwords()
		""" 
		TODO:
		add file: slovenian
		to folder: /home/user/nltk_data/corpora/stopwords/
		"""
		self.data_index = data_index

	def get_data(self):
		""" Function that reads data from html files, 
			extracts text content and does tokenization. """
		print("Fetching data ...")

		for root, dirs, files in os.walk(self.path, topdown=False):
			domain_key = root.split('/')[2]
			if domain_key != '':
				html = {}
				html_tokenized = {}
				for name in files:
					html_ending = name.split(".")
					if (html_ending[len(html_ending) - 1] == "html"):
						
						text = self.get_html_content(root, name)						
						
						# save original tokenized data
						html_text = nltk.word_tokenize(text)


						# tokenize text && remove stopwords && normalization
						tokenized_text = self.remove_stopwords(html_text)

						""" perform data indexing """
						####self.data_index.do_indexing(domain_key, name, html_text, tokenized_text)

						self.html_content[domain_key + "/" + name] = html_text

						html_tokenized[name] = tokenized_text
						html[name] = html_text
				
				self.html_tokenized_data[domain_key] = html_tokenized
				self.html_content_data[domain_key] = html

	def get_html_content(self, root, name):
		html_content = codecs.open(root+"/"+name, 'r', 'utf-8') 
		soup = BeautifulSoup(html_content, 'html.parser')
		# remove all script and style elements
		for script in soup(["script", "style"]):
		    script.extract()

		# get text
		text = soup.get_text()

		# break into lines and remove leading and trailing space on each
		lines = (line.strip() for line in text.splitlines())
		# break multi-headlines into a line each
		chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
		return ' '.join(x for x in chunks if x)

	def remove_stopwords(self, content):
		""" Function that removes punctuation and stopwords from website content.
			Also changes words to lowercase. """
		punctuation = ['.', ',','!','?','-','>','<',':',';',')','(','--','–', '/',"''",'','|','...','``','»','«']
		new_content_lcase = [x.lower() for x in content if x not in punctuation]
		new_content = list(filter(lambda x: True if x+" " not in \
						self.stopwords else False, new_content_lcase))
		return new_content

	def load_stopwords(self):
		# Stopwords from: https://github.com/nltk/nltk_data/issues/54
		return set(stopwords.words("slovenian"))



class DataIndexing:
	def __init__(self, db):
		self.db = db

	def word_freq(self, word, content):
		# returns count of word in content
		new_content_lcase = [x.lower() for x in content]
		return new_content_lcase.count(word)

	def list_to_str(self, idxs):
		# returns string of indxs '5,6,10'
		return ','.join(str(x) for x in idxs)

	def do_indexing(self, page_dir, p, content_og, content_tk):
		for word in content_tk:
			# get all indexes of word from original content
			idxs = [idx for idx, w in enumerate(content_og) \
					if word == w.lower()]
			# get frequency of word from original content
			freq = self.word_freq(word, content_og)
					
			# now this has to be saved to DB
			self.db.insert_index_word(word)
			self.db.insert_posting(word, page_dir+'/'+p, freq, self.list_to_str(idxs), word)


def data_retrival_with_index(querried_data, html_dict):

	return_data = ""
	for el in querried_data:
		querried_indices = el[2].split(',') #string of indices
		indices = [int(i) for i in querried_indices]
		indices.sort()
		querried_url = el[0]  #folder/url
		querried_freq = el[1] #frequency
		result = ""
		document = html_dict[querried_url]
		doc_length = len(document)
		i = 0
		while i < querried_freq:
			if (i > 4): break
			querried_i = indices[i]
			while((i+1) < len(indices) and querried_i + 3 >= indices[i+1]):
				i += 1
			result = result + " ... "
			if(querried_i - 3 >= 0): result += document[querried_i - 3] + " "
			if(querried_i - 2 >= 0): result += document[querried_i - 2] + " "
			if(querried_i - 1 >= 0): result += document[querried_i - 1] + " "
			result += document[querried_i] + " "
			if (querried_i + 1 < doc_length): result += document[querried_i + 1] + " "
			if (querried_i + 2 < doc_length): result +=	document[querried_i + 2] + " "
			if (querried_i + 3 < doc_length): result +=	document[querried_i + 3]
			i += 1

		return_data += '{:11} {:45} {} ...\n'.format(str(querried_freq), querried_url, result)
	return return_data


if __name__ == "__main__":
	print("I am alive.")

	# initialize db
	database = DataBase('db.sqlite')

	# initialize dataIndexing class
	data_index = DataIndexing(database)

	# initialize FileRead class with path and data_index object
	file_read = FileRead('../data/', data_index)
	# fetch data and perform data operations
	file_read.get_data()

	html_dict = file_read.html_content

	######Querrying

	##Query for predelovalne dejavosti:
	start = time.time()
	querried_data = database.get_querry_from_posting('predelovalne', 'dejavnosti', '', '', '')

	result = data_retrival_with_index(querried_data, html_dict)
	end = time.time()
	print('Results for a query: "predelovalne dejavnosti"\n')
	print("Result found in ", round((end - start) * 1000), "ms.\n")
	print('Frequencies Document                                       Snippet')
	print(
		'----------- ---------------------------------------------- -----------------------------------------------------------')
	print(result)

	##Query for trgovina:
	start = time.time()
	querried_data = database.get_querry_from_posting('trgovina','','', '', '')

	result = data_retrival_with_index(querried_data, html_dict)
	end = time.time()
	print('Results for a query: "trgovina"\n')
	print("Result found in ", round((end - start)*1000),"ms.\n")
	print('Frequencies Document                                       Snippet')
	print('----------- ---------------------------------------------- -----------------------------------------------------------')
	print(result)

	##Query for social services:
	start = time.time()
	querried_data = database.get_querry_from_posting('social', 'services', '', '', '')

	result = data_retrival_with_index(querried_data, html_dict)
	end = time.time()
	print('Results for a query: "social services"\n')
	print("Result found in ", round((end - start) * 1000), "ms.\n")
	print('Frequencies Document                                       Snippet')
	print('----------- ---------------------------------------------- -----------------------------------------------------------')
	print(result)


	##Query for statistični urad RS:
	start = time.time()
	querried_data = database.get_querry_from_posting('statistični', 'urad', 'rs', '', '')

	result = data_retrival_with_index(querried_data, html_dict)
	end = time.time()
	print('Results for a query: "statistični urad RS"\n')
	print("Result found in ", round((end - start) * 1000), "ms.\n")
	print('Frequencies Document                                       Snippet')
	print('----------- ---------------------------------------------- -----------------------------------------------------------')
	print(result)

	##Query for otroški dodatki in državna štipendija:
	start = time.time()
	querried_data = database.get_querry_from_posting('otroški', 'dodatki', 'državna', 'štipendija', '')

	result = data_retrival_with_index(querried_data, html_dict)
	end = time.time()
	print('Results for a query: "otroški dodatki in državne štipendije"\n')
	print("Result found in ", round((end - start) * 1000), "ms.\n")
	print('Frequencies Document                                       Snippet')
	print('----------- ---------------------------------------------- -----------------------------------------------------------')
	print(result)


	##Query for fakulteta:
	start = time.time()
	querried_data = database.get_querry_from_posting('fakulteta', '', '', '', '')

	result = data_retrival_with_index(querried_data, html_dict)
	end = time.time()
	print('Results for a query: "fakulteta"\n')
	print("Result found in ", round((end - start) * 1000), "ms.\n")
	print('Frequencies Document                                       Snippet')
	print(
		'----------- ---------------------------------------------- -----------------------------------------------------------')
	print(result)

	# close db connection
	database.close_conn()
	