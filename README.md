# IEPS Seminar 3

The goal of this assignment was to implement data preprocessing and indexing of given HTML documents and perform querying against it using two approaches: using inverted index and naive data retrieval.

## Prerequisites

- python version >= 3.6

## How to setup and run

- donwload zip or clone the project
- go into folder indexer

### install required packages

$ pip install -r requirements.txt

- add file: slovenian (located in the base directory) 
- to folder: /home/user/nltk_data/corpora/stopwords/

- when running the code for the first time UNCOMMENT in file indexer.py (line 67,68):
  - nltk.download('punkt')
  - nltk.download('stopwords')
  
- for data retrieval with inverted index run:
```
python indexer.py
```
- for naive data retrieval run:
```
python naive_data_retrieval.py.py
```
