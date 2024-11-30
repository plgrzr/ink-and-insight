from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

def preprocess_math_text(text):
    """
    Preprocess text containing mathematical content
    """
    # Replace common math symbols with words
    replacements = {
        '+': 'plus',
        '-': 'minus',
        '=': 'equals',
        '≠': 'not_equals',
        '≈': 'approximately',
        '∑': 'sum',
        '∫': 'integral',
        '×': 'times',
        '÷': 'divided_by',
        '^': 'power',
        '√': 'sqrt',
        '∞': 'infinity',
        '≤': 'less_equal',
        '≥': 'greater_equal',
        '<': 'less_than',
        '>': 'greater_than',
    }
    
    for symbol, word in replacements.items():
        text = text.replace(symbol, f' {word} ')
    
    # Handle LaTeX-style math expressions
    text = re.sub(r'\$(.*?)\$', r'\1', text)  # Remove math delimiters but keep content
    text = re.sub(r'\\[a-zA-Z]+', lambda m: m.group(0).replace('\\', ''), text)  # Remove backslashes from LaTeX commands
    
    # Remove special characters but keep alphanumeric and processed math symbols
    text = re.sub(r'[^a-zA-Z0-9\s_]', ' ', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    return text

def compute_text_similarity(text1, text2):
    """
    Compute similarity between two texts using TF-IDF and cosine similarity
    """
    try:
        # Preprocess texts
        processed_text1 = preprocess_math_text(text1)
        processed_text2 = preprocess_math_text(text2)
        
        print(f"Processed text 1: {processed_text1[:100]}")
        print(f"Processed text 2: {processed_text2[:100]}")
        
        # Check if texts are empty or identical
        if not processed_text1.strip() or not processed_text2.strip():
            print("One or both texts are empty after processing")
            return 0.0
        if processed_text1.strip() == processed_text2.strip():
            return 1.0
        
        # Configure vectorizer
        vectorizer = TfidfVectorizer(
            stop_words=None,
            min_df=1,
            analyzer='char_wb',  # Use character n-grams
            ngram_range=(3, 5),  # Use 3 to 5 character sequences
            lowercase=True
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform([processed_text1, processed_text2])
            vocabulary_size = len(vectorizer.vocabulary_)
            print(f"Vocabulary size: {vocabulary_size}")
            
            if vocabulary_size == 0:
                print("Warning: Empty vocabulary after vectorization")
                return 0.0
            
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(np.clip(similarity, 0, 1))
            
        except ValueError as e:
            print(f"Vectorization error: {str(e)}")
            return 0.0
            
    except Exception as e:
        print(f"Error computing text similarity: {str(e)}")
        return 0.0 