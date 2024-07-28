import os
import shutil
import pandas as pd
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec

# Function to clear Hugging Face cache
def clear_huggingface_cache():
    cache_path = os.path.expanduser('~/.cache/huggingface/hub')
    if os.path.exists(cache_path):
        shutil.rmtree(cache_path)
        print("Hugging Face cache cleared.")
    else:
        print("Hugging Face cache is already clear.")

# Clear the cache before downloading the model
clear_huggingface_cache()

# Initialize the Sentence Transformer model
try:
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
except Exception as e:
    print(f"Error initializing model: {e}")
    raise

# Initialize Pinecone

index_name = 'books'
from pinecone import Pinecone

pc = Pinecone(api_key="f5868cab-1450-4046-a9f9-1bb6480075bf")
index = pc.Index(index_name)

# Check if the index exists; if not, create it
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,  # 384 is the dimension for MiniLM model
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-west-2'
        )
    )

index = pc.Index(index_name)

# Read the CSV file
csv_file_path = 'new_books.csv'
df = pd.read_csv(csv_file_path)

# Print the head of the dataframe to check the data
print(df.head())

# Ensure there are no duplicate entries based on the unique identifier (e.g., book_id or index)
df = df.drop_duplicates()

# Generate embeddings and prepare data for Pinecone
batch_size = 100  # Process in batches to avoid overloading memory

total_vectors = 0

for i in range(0, len(df), batch_size):
    batch_end = min(i + batch_size, len(df))
    batch = df.iloc[i:batch_end]

    # Prepare the data for embedding
    texts = batch['all_text'].tolist()
    embeddings = model.encode(texts)

    # Prepare Pinecone upserts
    upserts = []
    for idx, embedding in enumerate(embeddings):
        # Convert year to integer if it's not NaN
        year = batch.iloc[idx]['published_year']
        year = int(year) if pd.notna(year) else None

        metadata = {
            'title': batch.iloc[idx]['title'],
            'author': batch.iloc[idx]['authors'],
            'description': batch.iloc[idx]['description'],
            'categories': batch.iloc[idx]['categories'],
            'year': year
        }
        upserts.append({
            'id': str(batch.index[idx]),  # Use the dataframe index as the unique ID
            'values': embedding.tolist(),
            'metadata': metadata
        })

    # Upsert the data into Pinecone
    index.upsert(vectors=upserts)
    
    # Log the number of vectors processed
    total_vectors += len(upserts)
    print(f"Processed {total_vectors} / {len(df)} vectors.")

print(f"All data has been processed and stored in Pinecone. Total vectors: {total_vectors}. Expected vectors: {len(df)}.")
