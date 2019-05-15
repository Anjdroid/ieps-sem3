import sqlite3
import os
from bs4 import BeautifulSoup
import codecs

class DataBase:
	def __init__(self, database):
		self.conn = sqlite3.connect(database)
		self.curr = self.conn.cursor()
		print("Connected to db.")

	def insert_index_word(self, text):
		self.curr.execute('INSERT INTO IndexWord (word) VALUES (?)', (text))
		print("Adding index word: ", text + "\n")

	def insert_posting(self, w, doc, freq, idxs, word_fk):
		self.curr.execute('INSERT INTO Posting (word, documentName, frequency, indexes, word) VALUES (?, ?, ?, ?, ?)', (w, doc, freq, idxs, word_fk))
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
	def __init__(self, path):
		self.path = path
		"""
			Dictionary for extracted text from html files:
			'dir_name' : {'website_name' : 'html_text'}
		"""
		self.html_content_data = {}

	def get_data(self):
		print("Fetching data ...")
		for root, dirs, files in os.walk(self.path, topdown=False):
			domain_key = root.split('/')[2]
			if domain_key != '':
				html = {}
				for name in files:
					html_ending = name.split(".")
					if (html_ending[len(html_ending) - 1] == "html"):
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
						text = ' '.join(chunk for chunk in chunks if chunk)
						html[name] = text
				self.html_content_data[domain_key] = html


if __name__ == "__main__":
	print("I am alive.")
	file_read = FileRead('../data/')
	file_read.get_data()
	
	# print(file_read.html_content_data)

	database = DataBase('db.sqlite')
	
	""" 
	DB CHECK:

	database.get_all_index_word()
	database.get_all_posting()
	database.insert_index_word("text")
	database.insert_posting("t1", "t2", 3, "t3", "text")
	database.get_all_index_word()
	database.get_all_posting()

	"""
	