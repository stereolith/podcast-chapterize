class Chapterizer:
    """Handle segmentation of a document with the cosine similarity method
    """
    def __init__(
        self,
        window_width=200,
        max_utterance_delta=90,
        tfidf_min_df=0,
        tfidf_max_df=0.59,
        savgol_window_length=0,
        savgol_polyorder=5,
        doc_vectorizer='ft_average'
    ):
        """init Chapterizer with hyperparameters
        
        Args:
            window_width (int, optional): width of initial segmentation. Defaults to default_params.window_width.
            max_utterance_delta (int, optional): maximum delta of tokens when refining detected boundaries by choosing nearby utterance boundaries. Defaults to default_params.max_utterance_delta.
            tfidf_min_df (int, optional): tfidf min_df value. Defaults to default_params.tfidf_min_df.
            tfidf_max_df (int, optional): tfidf max_df value. Defaults to default_params.tfidf_max_df.
            savgol_window_length (int, optional): window_length value for savgol smoothing. Defaults to default_params.savgol_window_length.
            savgol_polyorder (int, optional): polyorder value for savgol smoothing. Defaults to default_params.savgol_polyorder.
        """    
        self.window_width = window_width
        self.max_utterance_delta = max_utterance_delta
        self.tfidf_min_df = tfidf_min_df
        self.tfidf_max_df = tfidf_max_df
        self.savgol_window_length = savgol_window_length
        self.savgol_polyorder = savgol_polyorder
        self.doc_vectorizer = doc_vectorizer

    def chapterize(
        self,
        tokens,
        ft_en,
        ft_de,
        boundaries=[],
        language='en',
        visual=False
        ):
        """segment a document into coherent parts, using a TextTiling-inspired method
        
        Args:
            tokens (TranscriptToken): tokens to segment
            boundaries (list, optional): list of integers, additional boundaries to refine segmentation. Defaults to [].
            language (str, optional): language (ISO 639-1 language code). Defaults to 'en'.
            visual (bool, optional): show graph. Defaults to False.
        
        Returns:
            [type]: [description]
        """    

        from chapterize.preprocessor_helper import lemma
        from chapterize.document_vectorizer import DocumentVectorizer
        from write_chapters import Chapter

        import nltk
        from sklearn.metrics.pairwise import linear_kernel
        import numpy as np
        from scipy.signal import savgol_filter
        from scipy.signal import argrelextrema
        from math import floor
        import json

        # preprocess: 
        # lowercase, lemmatize, remove stopwords
        # segment transcript into segments of window_width

        processed = [] # segments of width window_width
        end_times = [] # end times of every segment

        # batch preprocess tokens
        chunk_tokens_lemma = lemma([token.token for token in tokens], language)
        for i, token in enumerate(tokens):
            token.token = chunk_tokens_lemma[i]

        chunks = list(divide_chunks(tokens, self.window_width))
        for chunk in chunks:       
            processed_section = []
            for token in chunk:
                processed_section.append(token.token)
                last_end_time = token.time
            processed.append(processed_section)
            end_times.append(last_end_time)

        end_times.pop()

        # vectorize
        #dv = DocumentVectorizer('tfidf', tfidf_min_df=default_params.tfidf_min_df, tfidf_max_df=default_params.tfidf_max_df)
        
        dv = DocumentVectorizer(self.tfidf_min_df, self.tfidf_max_df, ft_en, ft_de)
        document_vectors = dv.vectorize_docs(self.doc_vectorizer, processed, language=language)

        print(document_vectors.shape[0])

        # calculate cosine similarity score for adjacent segments
        cosine_similarities = []
        print('\ncosine similarity scores:')
        for i, doc_vec in enumerate(document_vectors[:-1]):
            cosine_similarity = linear_kernel(doc_vec, document_vectors[i+1])[0][0]
            cosine_similarities.append(cosine_similarity)
            print(cosine_similarity)


        # smooth curve with Savitzky-Golay filter
        if self.savgol_window_length == 0:
            self.savgol_window_length = min(9, len(cosine_similarities))
            if self.savgol_window_length % 2 == 0: self.savgol_window_length -= 1
        cosine_similarities_smooth = savgol_filter(cosine_similarities, self.savgol_window_length, self.savgol_polyorder)

        # calculate local minima
        minima = argrelextrema(cosine_similarities_smooth, np.less)[0]
        print('\nlocal minima found at {}\n'.format(minima))

        self.max_utterance_delta = floor(self.window_width*.4)

        # concatinate tokens
        concat_segments = []
        for i, minimum in enumerate(minima):
            concat_segment = ''
            if i == 0:
                print(f'concat processed from 0 to {minimum+1} ({processed[0: minimum + 1]})')
                concat_segment += " ".join(processed[0: minimum + 1])
            else:
                concat_segment += " ".join(processed[minima[i-1] + 1 : minimum + 1])
            concat_segments.append(concat_segment)
        concat_segments.append(" ".join(processed[minima[-1] + 1:])) # append last section (from last boundary to end)
        
        #find closest utterance boundary for each local minima
        segment_boundary_tokens = []
        segment_boundary_times = []
        for minimum in minima:
            closest = min(boundaries, key=lambda x:abs(x-((minimum + 1)*self.window_width)))
            print('for minimum at token {}, closest utterance boundary is at token {}'.format((minimum+1)*self.window_width, closest))

            if abs((minimum+1)*self.window_width - closest) <= self.max_utterance_delta:
                segment_boundary_tokens.append(tokens[closest].token)
                segment_boundary_times.append(tokens[closest].time)
            else:
                print('  closest utterance boundary is too far from minimum boundary (max_utterance_delta exceeded), topic boundary set to {}'.format(tokens[minimum*self.window_width].token))
                segment_boundary_tokens.append(tokens[(minimum+1)*self.window_width].token)
                segment_boundary_times.append(tokens[(minimum+1)*self.window_width].time)

        # print("Segment boundary tokens:\n", segment_boundary_tokens)

        if visual:
            visualize(cosine_similarities_smooth, cosine_similarities, minima, segment_boundary_times, end_times)

        boundary_indices = [0] + [minimum*self.window_width for minimum in minima]

        return concat_segments, boundary_indices

def divide_chunks(l, n):
    for i in range(0, len(l), n):  
        yield l[i:i + n]

def visualize(cosine_similarities, cosine_similarities_raw, minima, segment_boundary_times, end_times): 
    import matplotlib.pyplot as plt

    end_times = [time / 60 for time in end_times]

    minimaX = [np.array(end_times)[minimum] for minimum in minima]
    minimaY = [cosine_similarities[minimum] for minimum in minima]

    fig, ax = plt.subplots(figsize=(13, 6))

    plt.plot(end_times, cosine_similarities_raw, 'lightblue', label='cosine similarity', zorder=0)
    plt.plot(end_times, cosine_similarities, marker='.', label='smoothed cosine similarity', zorder=1)
    plt.scatter(minimaX, minimaY, c='red', label='local minimum', zorder=2)

    for x in segment_boundary_times:
        plt.axvline(x=x/60)

    ax.legend()
    plt.ylabel('cosine similarity')
    plt.xlabel('time in minutes')
    plt.show()
