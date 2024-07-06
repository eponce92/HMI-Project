import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from langdetect import detect
from fuzzywuzzy import fuzz

class SemanticSearch:
    def __init__(self, similarity_threshold=0.3):
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2', device='cpu')
        self.product_embeddings = None
        self.products = None
        self.similarity_threshold = similarity_threshold
        print(f"DEBUG: SemanticSearch initialized with threshold {similarity_threshold}")

    def index_products(self, products):
        self.products = products
        texts = [f"{p['name']} {p.get('description', '')}" for p in products]
        self.product_embeddings = self.model.encode(texts)
        print(f"DEBUG: Indexed {len(products)} products")

    def search(self, query, top_k=10):
        print(f"DEBUG: Searching for query: '{query}'")
        query_terms = [term.strip() for term in query.split(',') if term.strip()]
        query_embeddings = self.model.encode(query_terms)
        similarities = cosine_similarity(query_embeddings, self.product_embeddings)
        max_similarities = np.max(similarities, axis=0)
        
        combined_scores = []
        for i, product in enumerate(self.products):
            semantic_score = max_similarities[i]
            fuzzy_score = max(fuzz.partial_ratio(query.lower(), product['name'].lower()) / 100,
                              fuzz.partial_ratio(query.lower(), product.get('description', '').lower()) / 100)
            combined_score = max(semantic_score, fuzzy_score)
            combined_scores.append(combined_score)
            print(f"DEBUG: Product '{product['name']}' - Semantic Score: {semantic_score:.4f}, Fuzzy Score: {fuzzy_score:.4f}, Combined Score: {combined_score:.4f}")

        top_indices = np.argsort(combined_scores)[-top_k:][::-1]
        results = [
            {**self.products[i], 'similarity': float(combined_scores[i])}
            for i in top_indices if combined_scores[i] >= self.similarity_threshold
        ]
        
        print(f"DEBUG: Found {len(results)} results above threshold {self.similarity_threshold}")
        for result in results:
            print(f"DEBUG: Included result: '{result['name']}' with similarity {result['similarity']:.4f}")
        
        return results

    def check_exclude_similarity(self, product_text, exclude_words):
        if not exclude_words:
            return False
        exclude_terms = [term.strip() for term in exclude_words if term.strip()]
        product_embedding = self.model.encode([product_text])
        exclude_embeddings = self.model.encode(exclude_terms)
        similarities = cosine_similarity(product_embedding, exclude_embeddings)[0]
        should_exclude = any(sim > self.similarity_threshold for sim in similarities)
        print(f"DEBUG: Checking exclusion for '{product_text}' against {exclude_terms}. Should exclude: {should_exclude}")
        return should_exclude

def preprocess_query(query):
    return query.lower().strip()