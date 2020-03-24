from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

def chapter_names(segments, title_tokens=6):
    """generate chapter titles for a segmented document
    
    Args:
        segments (list of strings): segmented document
        title_tokens (int, optional): Number of tokens per chapter title. Defaults to 6.

    Returns:
        list of strings: chapter titles
    """
    
    concat_vectorizer = TfidfVectorizer(max_df=0.7)
    concat_tfidf = concat_vectorizer.fit_transform(segments)
    
    # get top 6 tokens with the highest tfidf-weighted score for each combined section 
    top_tokens = []
    feature_names = np.array(concat_vectorizer.get_feature_names())
    for doc in concat_tfidf:
        tfidf_sorted = np.argsort(doc.toarray()).flatten()[::-1]
        top_token_list = feature_names[tfidf_sorted][:title_tokens].tolist()
        top_tokens.append(" ".join(top_token_list))
        
    return top_tokens