import sqlite3
import os
from bs4 import BeautifulSoup
import codecs
import nltk
from nltk.corpus import stopwords


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
						self.data_index.do_indexing(domain_key, name, html_text, tokenized_text)

						#
						# OPTIONAL BREAK FOR TESTING (only one document)
						break
						#

						# not sure we still need to save all this?
						html_tokenized[name] = tokenized_text
						html[name] = tokenized_text
				# not sure we still need to save all this?
				self.html_tokenized_data[domain_key] = html_tokenized
				self.html_content_data[domain_key] = html

	def get_html_content(self, root, name):
		html_content = codecs.open(root+"/"+name, 'r', 'utf-8') 
		soup = BeautifulSoup(html_content)
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
		punctuation = ['.', ',','!','?','-','>','<',':',';',')','(','--','–', '/',"''",'']
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
		return content.count(word)

	def list_to_str(self, idxs):
		# returns string of indxs '5,6,10'
		return ','.join(str(x) for x in idxs)

	def do_indexing(self, page_dir, p, content_og, content_tk):
		for word in content_tk:
			# get all indexes of word from original content
			idxs = [idx for idx, w in enumerate(content_og) \
					if word == w]
			# get frequency of word from original content
			freq = self.word_freq(word, content_og)
					
			# now this has to be saved to DB
			self.db.insert_index_word(word)
			self.db.insert_posting(word, page_dir+'/'+p, freq, self.list_to_str(idxs), word)
			# TODO: CHECK DB?



if __name__ == "__main__":
	print("I am alive.")

	# initialize db
	database = DataBase('db.sqlite')

	"""
	# check what is in db
	database.get_all_index_word()
	database.get_all_posting()
	"""

	# initialize dataIndexing class
	data_index = DataIndexing(database)

	# initialize FileRead class with path and data_index object
	file_read = FileRead('../data/', data_index)
	# fetch data and perform data operations
	file_read.get_data()

	# check what is in db
	database.get_all_index_word()
	database.get_all_posting()

	""" 
	DB CHECK:

	database.get_all_index_word()
	database.get_all_posting()
	database.insert_index_word("text")
	database.insert_posting("t1", "t2", 3, "t3", "text")
	database.get_all_index_word()
	database.get_all_posting()

	"""

	# close db connection
	database.close_conn()
	