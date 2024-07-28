from langchain_core.documents import Document
from langchain_chroma import Chroma
from sentence_transformers import SentenceTransformer
from langchain.embeddings.base import Embeddings
from typing import List
import pandas as pd

class SentenceTransformerEmbeddings(Embeddings):
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts).tolist()
    
    def embed_query(self, text: str) -> List[float]:
        return self.model.encode([text])[0].tolist()
    
path = "/Users/hboukhamse001/Desktop/projects/lang_chain_intro/app/books.csv"
book_data = pd.read_csv(path)
for column in book_data.columns:
    if column in ['title', 'subtitle', 'authors', 'categories', 'description']:
        book_data[column] = book_data[column].fillna("Unknown")
book_data = book_data[[col for col in book_data.columns if col not in ["isbn13", "isbn10", "thumbnail"]]]
book_data["ratings_count"] = book_data["ratings_count"].fillna(book_data["ratings_count"].mean())
book_data["num_pages"] = book_data["num_pages"].fillna(book_data["num_pages"].mean())
book_data["average_rating"] = book_data["average_rating"].fillna(book_data["average_rating"].mean())
book_data["published_year"] = book_data["published_year"].fillna(book_data["published_year"].mean())

def get_document(title, subtitle, authors, categories, description, published_year, average_rating, num_pages, ratings_count):
    document_content = f'''The book's title is {title}, and the subtitle is {subtitle}. It is written by {authors} in {published_year}. The category of the book is {categories} and it is described as {description}, and has a rating of {average_rating} based on {ratings_count} ratings. It is also {num_pages} long.'''
    return document_content

documents = []
for i in range(len(book_data)):
    title, subtitle, authors, categories, description, published_year, average_rating, num_pages, ratings_count  = book_data.iloc[i].tolist()
    document_content = get_document(title, subtitle, authors, categories, description, published_year, average_rating, num_pages, ratings_count)
    documents.append(
        Document(
            page_content=document_content,
            metadata={
               "title":title,
               "subtitle":subtitle,
               "authors":authors,
               "categories":categories,
               "description":description,
               "published_year":published_year,
               "average_rating":average_rating, 
               "num_pages":num_pages,
               "ratings_count":ratings_count,
            }
        )
    )

vectorstore = Chroma.from_documents(
    documents,
    embedding=SentenceTransformerEmbeddings("all-MiniLM-L6-v2"),
    persist_directory="../chroma_db"
)

base_retriever = vectorstore.as_retriever(search_kwargs={'k': 7})
