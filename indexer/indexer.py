import sqlite3
import os
from bs4 import BeautifulSoup
import codecs

class DataBase:
	def __init__(self, database):
		self.conn = sqlite3.connect(database)
		self.c = self.conn.cursor()
		print("Connected to db.")

	def commit_db(self):
		self.conn.commit()
		print("Data is commited.")

	def close_conn(self):
		self.conn.close()
		print("Connection to db closed.")

class FileRead:
	def __init__(self, path):
		self.path = path
		self.html_content_data = {}

	def get_data(self):
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
	