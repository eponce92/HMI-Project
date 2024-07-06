import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class SemanticSearch:
    def __init__(self):
        # Set the Hugging Face cache directory to a specific location
        os.environ['TRANSFORMERS_CACHE'] = os.path.join(os.path.expanduser('~'), '.cache', 'huggingface')
        
        try:
            # Load a pre-trained BERT model for semantic similarity, forcing CPU usage
            self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2', device='cpu')
        except Exception as e:
            print(f"Error initializing SentenceTransformer: {e}")
            raise
        
        self.product_embeddings = None
        self.products = None

    def index_products(self, products):
        self.products = products
        # Create embeddings for all product names and descriptions
        texts = [f"{p['name']} {p.get('description', '')}" for p in products]
        self.product_embeddings = self.model.encode(texts)

    def search(self, query, top_k=10):
        # Encode the search query
        query_embedding = self.model.encode([query])

        # Calculate cosine similarity between query and all products
        similarities = cosine_similarity(query_embedding, self.product_embeddings)[0]

        # Get the indices of the top-k most similar products
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        # Return the top-k most similar products with their similarity scores
        return [
            {**self.products[i], 'similarity': float(similarities[i])}
            for i in top_indices
        ]

def preprocess_query(query):
    # Here you can add more sophisticated query preprocessing if needed
    return query.lower().strip()

# Usage example:
# semantic_search = SemanticSearch()
# semantic_search.index_products(scraped_products)
# results = semantic_search.search("healthy breakfast cereal")