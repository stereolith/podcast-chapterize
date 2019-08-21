import nltk
from nltk.stem import WordNetLemmatizer 
import nltk
nltk.download('wordnet')

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

import numpy as np
from scipy.signal import savgol_filter
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt

import json

def cosine_similarity(transcriptFile, windowWidth=300, visual=True):
    try:
        with open(transcriptFile, "r") as f:
            transcript = json.loads(f.read())
    except OSError:
        print("File not found")
        return
    
    # preprocess: 
    # lowercase, lemmatize, remove stopwords
    # segment transcript into segments of windowWidth

    flattenTranscript = [token for section in transcript for token in section]

    processed = [] # segments of width windowWidth
    endTimes = [] # end times of every segment
    utteranceBoundaries = [] # index of last token in each utterance

    lemmatizer = WordNetLemmatizer()
    totalTokenCount = 0
    tokenCount = 0
    processedSection = ''
    for section in transcript:
        for token in section:
            totalTokenCount += 1
            tokenCount += 1
            if tokenCount > windowWidth:
                processed.append(processedSection)
                endTimes.append(token['startTime'])
                processedSection = ''
                tokenCount = 0
            processedSection += ' ' + lemmatizer.lemmatize(token['word']).lower()
        utteranceBoundaries.append(totalTokenCount)

    endTimes.pop()

    # vectorize, remove of stopwords and weigh by tf-idf
    vectorizer = TfidfVectorizer(min_df=4, max_df=0.95, stop_words='english')
    tfidf = vectorizer.fit_transform(processed)
    # tfidf matrix: rows: documents, columns: words

    # calculate cosine similarity score for adjacent segments
    cosine_similarities = []
    for i, doc_vec in enumerate(tfidf[:-1]):
        cosine_similarity = linear_kernel(doc_vec, tfidf[i+1])[0][0]
        cosine_similarities.append(cosine_similarity)
        print(cosine_similarity)

    # smooth curve with Savitzky-Golay filter
    window_length = min(11, len(cosine_similarities))
    if window_length % 2 == 0: window_length -= 1
    cosine_similarities_smooth = savgol_filter(cosine_similarities, window_length, 4)

    # calculate local minima
    minima = argrelextrema(cosine_similarities_smooth, np.less)[0]
    print('local minima found at ', minima)

    #find closest utterance boundary for each local minima
    segmentBoundaryTokens = []
    segmentBoundaryTimes = []
    for minimum in minima:
        closest = min(utteranceBoundaries, key=lambda x:abs(x-(minimum*windowWidth)))
        segmentBoundaryTokens.append(flattenTranscript[closest])
        segmentBoundaryTimes.append(flattenTranscript[closest]['startTime'])
        print('for minimum at token {}, closest utterance boundary is at token {}'.format(minimum*windowWidth, closest))

    if visual:
        visualize(cosine_similarities_smooth, cosine_similarities, minima, segmentBoundaryTokens, endTimes)

    return segmentBoundaryTimes

def visualize(cosine_similarities, cosine_similarities_raw, minima, segmentBoundaryTokens, endTimes): 
    endTimes = [time / 60 for time in endTimes]

    minimaX = [np.array(endTimes)[minimum] for minimum in minima]
    minimaY = [cosine_similarities[minimum] for minimum in minima]

    segmentBoundaryTokensX = [token['startTime']/60 for token in segmentBoundaryTokens]

    fig, ax = plt.subplots(figsize=(13, 6))

    plt.plot(endTimes, cosine_similarities_raw, 'lightblue', label='cosine similarity', zorder=0)
    plt.plot(endTimes, cosine_similarities, marker='.', label='smoothed cosine similarity', zorder=1)
    plt.scatter(minimaX, minimaY, c='red', label='local minimum', zorder=2)
    for x in segmentBoundaryTokensX:
        plt.axvline(x=x)

    ax.legend()
    plt.ylabel('cosine similarity')
    plt.xlabel('time in minutes')
    plt.show()

