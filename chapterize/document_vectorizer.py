class DocumentVectorizer:
    """vectorize a list of documents
    
    Returns:
        scipy.sparse.csr.csr_matrix: document vectors (x: documents)
    """

    def __init__(self, tfidf_min_df, tfidf_max_df, processed_ft_vectors):
        """initialize a DocumentVectorizer with hyperparameters
        
        Args:
            tfidf_min_df (int, optional): tfidf min_df value. Defaults to default_params.tfidf_min_df.
            tfidf_max_df (int, optional): tfidf max_df value. Defaults to default_params.tfidf_max_df.
        """        
        self.tfidf_min_df = tfidf_min_df
        self.tfidf_max_df = tfidf_max_df
        self.processed_ft_vectors = processed_ft_vectors

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
        elif method == 'ft_sif_average':
            return self._fasttext_sif_weighted_average_vectorizer
        else:
            raise ValueError(method)

    def _tfidf_vectorizer(self, documents, language):
        from sklearn.feature_extraction.text import TfidfVectorizer

        documents = [" ".join(doc) for doc in documents]

        if self.tfidf_min_df == 0:
            self.tfidf_min_df = 1 if len(documents) < 7 else 4
        vectorizer = TfidfVectorizer(min_df=self.tfidf_min_df, max_df=self.tfidf_max_df)
        return vectorizer.fit_transform(documents)

    def _fasttext_average_vectorizer(self, documents, language):
        import numpy as np
        from scipy import sparse
        
        ft_doc_vectors = fasttext_vectors(documents, language, self.processed_ft_vectors)
        
        average_document_vectors = []
        for word_vectors in ft_doc_vectors:
            mean_vec = np.mean( np.array(word_vectors), axis=0 )
            average_document_vectors.append(mean_vec)

        return sparse.csr.csr_matrix(average_document_vectors)

    def _fasttext_sif_weighted_average_vectorizer(self, documents, language):
        from collections import Counter
        import itertools
        import numpy as np
        from scipy import sparse

        # sif weights
        concat_documents = itertools.chain.from_iterable(([document for document in documents]))
        word_counts = Counter(concat_documents)
        a = 1e-4
        sif_weights = {word: a/(a+word_counts[word]) for word in word_counts}
        
        # FastText vectors
        ft_doc_vectors = fasttext_vectors(documents, language, self.processed_ft_vectors)
        
        average_document_vectors = []
        for i, word_vectors in enumerate(ft_doc_vectors):
            weightes_ft_vectors = [ft_vec * sif_weights[documents[i][j]] for j, ft_vec in enumerate(word_vectors)]
            mean_vec = np.mean( np.array(weightes_ft_vectors), axis=0 )
            average_document_vectors.append(mean_vec)

        return sparse.csr.csr_matrix(average_document_vectors)  


    def _fasttext_sum_vectorizer(self, documents, language):
        import numpy as np
        from scipy import sparse
        
        ft_doc_vectors = fasttext_vectors(documents, language, self.processed_ft_vectors)
        
        average_document_vectors = []
        for word_vectors in ft_doc_vectors:
            mean_vec = np.sum( np.array(word_vectors), axis=0 )
            average_document_vectors.append(mean_vec)

        return sparse.csr.csr_matrix(average_document_vectors)

def fasttext_vectors(documents, language, processed_ft_vectors):
    document_vectors = []
    
    for doc_i, document in enumerate(documents):
        ft_doc_vec = [processed_ft_vectors[doc_i][token_i] for token_i, token in enumerate(document)]
        document_vectors.append(ft_doc_vec)

    return document_vectors
