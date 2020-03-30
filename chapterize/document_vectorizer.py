class DocumentVectorizer:
    """vectorize a list of documents
    
    Returns:
        scipy.sparse.csr.csr_matrix: document vectors (x: documents)
    """

    def __init__(self, tfidf_min_df, tfidf_max_df):
        """initialize a DocumentVectorizer with hyperparameters
        
        Args:
            tfidf_min_df (int, optional): tfidf min_df value. Defaults to default_params.tfidf_min_df.
            tfidf_max_df (int, optional): tfidf max_df value. Defaults to default_params.tfidf_max_df.
        """        
        self.tfidf_min_df = tfidf_min_df
        self.tfidf_max_df = tfidf_max_df

    def vectorize_docs(self, method, documents, language='en'):
        vectorizer = self.get_document_vectorizer(method)
        return vectorizer(documents, language)

    def get_document_vectorizer(self, method):
        if method == 'tfidf':
            return self._tfidf_vectorizer
        elif method == 'ft_average':
            return self._fasttext_average_vectorizer
        elif method == 'ft_sum':
            return self._fasttext_sum_vectorizer
        else:
            raise ValueError(method)

    def _tfidf_vectorizer(self, documents, language):
        from sklearn.feature_extraction.text import TfidfVectorizer

        if self.tfidf_min_df == 0:
            self.tfidf_min_df = 1 if len(documents) < 7 else 4
        vectorizer = TfidfVectorizer(min_df=self.tfidf_min_df, max_df=self.tfidf_max_df)
        return vectorizer.fit_transform(documents)

    def _fasttext_average_vectorizer(self, documents, language):
        import numpy as np
        from scipy import sparse
        
        ft_doc_vectors = fasttext_vectors(documents, language)
        
        average_document_vectors = []
        for word_vectors in ft_doc_vectors:
            mean_vec = np.mean( np.array(word_vectors), axis=0 )
            average_document_vectors.append(mean_vec)

        return sparse.csr.csr_matrix(average_document_vectors)

    def _fasttext_sum_vectorizer(self, documents, language):
        import numpy as np
        from scipy import sparse
        
        ft_doc_vectors = fasttext_vectors(documents, language)
        
        average_document_vectors = []
        for word_vectors in ft_doc_vectors:
            mean_vec = np.sum( np.array(word_vectors), axis=0 )
            average_document_vectors.append(mean_vec)

        return sparse.csr.csr_matrix(average_document_vectors)

def fasttext_vectors(documents, language):
    import fasttext
    import fasttext.util

    # check for deployment: 
    if language == 'en':
        model_path = fasttext.util.download_model('en', if_exists='ignore')
        ft = fasttext.load_model(model_path)
    elif language == 'de':
        model_path = fasttext.util.download_model('de', if_exists='ignore')
        ft = fasttext.load_model(model_path)
    else:
        raise ValueError(language)

    document_vectors = []
    
    for document in documents:
        ft_doc_vec = [ft[token] for token in document]
        document_vectors.append(ft_doc_vec)

    return document_vectors

