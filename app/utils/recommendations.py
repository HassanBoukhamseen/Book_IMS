import os
import pandas as pd
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec

# Initialize the Sentence Transformer model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Initialize Pinecone
api_key = os.environ.get("PINECONE_API_KEY")
pc = Pinecone(api_key=api_key)

index_name = 'books'
index = pc.Index(index_name)

def get_recommended_books(query, top_k=5):
    # Generate embedding for the query
    query_embedding = model.encode([query])[0]
    
    # Query Pinecone for similar embeddings
    results = index.query(
        vector=query_embedding.tolist(),
        top_k=top_k,
        include_metadata=True
    )
    
    # Extract and return the metadata of the top results
    recommended_books = []
    for match in results.matches:
        recommended_books.append({
            'title': match.metadata['title'],
            'author': match.metadata['author'],
            'description': match.metadata['description'],
            'categories': match.metadata['categories'],
            'year': match.metadata['year'],
            'score': match.score
        })
    
    return recommended_books

def format_recommended_books(recommended_books):
    """
    Convert the dictionary of recommended books into a single formatted string.

    Args:
        recommended_books (list of dict): List of recommended books with metadata.

    Returns:
        str: Single formatted string of recommended books.
    """
    formatted_books = ""
    for book in recommended_books:
        formatted_books += (
            f"Title: {book['title']}\n"
            f"Author: {book['author']}\n"
            f"Description: {book['description']}\n"
            f"Categories: {book['categories']}\n"
            f"Year: {book['year']}\n"
            f"Score: {book['score']}\n\n"
        )
    return formatted_books

# Example usage
# user_query = "A story about a futuristic world with advanced technology"
# recommended_books = get_recommended_books(user_query)

# for book in recommended_books:
#     print(f"Title: {book['title']}")
#     print(f"Author: {book['author']}")
#     print(f"Description: {book['description']}")
#     print(f"Categories: {book['categories']}")
#     print(f"Year: {book['year']}")
#     print(f"Score: {book['score']}\n")


