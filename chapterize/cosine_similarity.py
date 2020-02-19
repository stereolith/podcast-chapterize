import nltk

from chapterize.preprocessor_helper import stem
from write_chapters import Chapter

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

import numpy as np
from scipy.signal import savgol_filter
from scipy.signal import argrelextrema
from math import floor

import json

def cosine_similarity(tokens, boundaries=[], language='en', windowWidth=200, maxUtteranceDelta=90, visual=True):

    # preprocess: 
    # lowercase, lemmatize, remove stopwords
    # segment transcript into segments of windowWidth

    processed = [] # segments of width windowWidth
    end_times = [] # end times of every segment

    chunks = list(divide_chunks(tokens, windowWidth))

    for chunk in chunks:
        processed_section = ''
        for token in chunk:
            processed_section += ' ' + stem(token.token, language).lower()
            last_end_time = token.time
        processed.append(processed_section)
        end_times.append(last_end_time)

    end_times.pop()

    # vectorize, remove of stopwords and weigh by tf-idf
    min_df = 1 if len(processed) < 7 else 4
    vectorizer = TfidfVectorizer(min_df=min_df, max_df=0.95)
    tfidf = vectorizer.fit_transform(processed)
    # tfidf matrix: rows: documents, columns: words


    # calculate cosine similarity score for adjacent segments
    cosine_similarities = []
    print('\ncosine similarity scores:')
    for i, doc_vec in enumerate(tfidf[:-1]):
        cosine_similarity = linear_kernel(doc_vec, tfidf[i+1])[0][0]
        cosine_similarities.append(cosine_similarity)
        print(cosine_similarity)


    # smooth curve with Savitzky-Golay filter
    window_length = min(9, len(cosine_similarities))
    if window_length % 2 == 0: window_length -= 1
    cosine_similarities_smooth = savgol_filter(cosine_similarities, window_length, 5)

    # calculate local minima
    minima = argrelextrema(cosine_similarities_smooth, np.less)[0]
    print('\nlocal minima found at {}\n'.format(minima))

    maxUtteranceDelta = floor(windowWidth*.4)

    # find most common tokens for each section between minima by running tfidf weighing on combined sections
    concat_segments = []
    for i, minimum in enumerate(minima):
        concat_segment = ''
        if i == 0:
            concat_segment += " ".join(processed[0: minimum + 1])
        else:
            concat_segment += " ".join(processed[minima[i-1] + 1 : minimum + 1])
        concat_segments.append(concat_segment)
    concat_segments.append(" ".join(processed[minima[-1] + 1:])) # append last section (from last boundary to end)
    
    concat_vectorizer = TfidfVectorizer(max_df=0.7)
    concat_tfidf = concat_vectorizer.fit_transform(concat_segments)
    
    # get top 6 tokens with the highest tfidf-weighted score for each combined section 
    topTokens = []
    feature_names = np.array(concat_vectorizer.get_feature_names())
    for doc in concat_tfidf:
        tfidf_sorted = np.argsort(doc.toarray()).flatten()[::-1]
        topTokens.append(feature_names[tfidf_sorted][:6].tolist())
    

    #find closest utterance boundary for each local minima
    segment_boundary_tokens = []
    segment_boundary_times = []
    for minimum in minima:
        closest = min(boundaries, key=lambda x:abs(x-((minimum + 1)*windowWidth)))
        print('for minimum at token {}, closest utterance boundary is at token {}'.format((minimum+1)*windowWidth, closest))

        if abs((minimum+1)*windowWidth - closest) <= maxUtteranceDelta:
            segment_boundary_tokens.append(tokens[closest].token)
            segment_boundary_times.append(tokens[closest].time)
        else:
            print('  closest utterance boundary is too far from minimum boundary (maxUtteranceDelta exceeded), topic boundary set to {}'.format(tokens[minimum*windowWidth].token))
            segment_boundary_tokens.append(tokens[(minimum+1)*windowWidth].token)
            segment_boundary_times.append(tokens[(minimum+1)*windowWidth].time)

    # print("Segment boundary tokens:\n", segment_boundary_tokens)

    if visual:
        visualize(cosine_similarities_smooth, cosine_similarities, minima, segment_boundary_times, end_times)

    # prepare chapter/ title list
    chapters = []
    chapters.append(Chapter(0, " ".join(topTokens[0])))
    for i, time in enumerate(segment_boundary_times):
        chapters.append(Chapter(time, " ".join(topTokens[i+1])))

    return chapters

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

