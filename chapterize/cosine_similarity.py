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
    
    concat_vectorizer = TfidfVectorizer(stop_words='english')
    concat_tfidf = concat_vectorizer.fit_transform(concat_segments)
    
    # get top 6 tokens with the highest tfidf-weighted score for each combined section 
    topTokens = []
    feature_names = np.array(concat_vectorizer.get_feature_names())
    for doc in concat_tfidf:
        tfidf_sorted = np.argsort(doc.toarray()).flatten()[::-1]
        topTokens.append(feature_names[tfidf_sorted][:6].tolist())
    

    #find closest utterance boundary for each local minima
    segmentBoundaryTokens = []
    segmentBoundaryTimes = []
    for minimum in minima:
        closest = min(utteranceBoundaries, key=lambda x:abs(x-((minimum + 1)*windowWidth)))
        segmentBoundaryTokens.append(flattenTranscript[closest])
        segmentBoundaryTimes.append(flattenTranscript[closest]['startTime'])
        print('for minimum at token {}, closest utterance boundary is at token {}'.format(minimum*windowWidth, closest))

    if visual:
        visualize(cosine_similarities_smooth, cosine_similarities, minima, segmentBoundaryTimes, endTimes)


    # prepare chapter/ name list
    chapters = [{'time': 0, 'name': " ".join(topTokens[0])}]
    for i, time in enumerate(segmentBoundaryTimes):
        chapters.append({'time': time, 'name': " ".join(topTokens[i+1])})

    d3export(endTimes, vectorizer, tfidf, transcriptFile)

    #return [endTimes, vectorizer, tfidf]
    return chapters

def visualize(cosine_similarities, cosine_similarities_raw, minima, segmentBoundaryTimes, endTimes): 
    endTimes = [time / 60 for time in endTimes]

    minimaX = [np.array(endTimes)[minimum] for minimum in minima]
    minimaY = [cosine_similarities[minimum] for minimum in minima]

    fig, ax = plt.subplots(figsize=(13, 6))

    plt.plot(endTimes, cosine_similarities_raw, 'lightblue', label='cosine similarity', zorder=0)
    plt.plot(endTimes, cosine_similarities, marker='.', label='smoothed cosine similarity', zorder=1)
    plt.scatter(minimaX, minimaY, c='red', label='local minimum', zorder=2)

    for x in segmentBoundaryTimes:
        plt.axvline(x=x/60)

    ax.legend()
    plt.ylabel('cosine similarity')
    plt.xlabel('time in minutes')
    plt.show()

def d3export(endTimes, vectorizer, tfidf, transcriptFile):

    import os

    startTimes = endTimes.insert(0, 0)
    # get top x tokens with the highest tfidf-weighted score 
    feature_names = np.array(vectorizer.get_feature_names())
    topTokens = []
    for i, doc in enumerate(tfidf):
        tfidf_sorted_indices = np.argsort(doc.toarray()).flatten()[::-1]
        tfidf_sorted_scores =  np.sort(doc.toarray()).flatten()[::-1]
        zipped = zip(tfidf_sorted_indices, tfidf_sorted_scores)
        topTokens.append({
            'tokens': [{
                'token': feature_names[token[0]],
                'score': token[1]
            } for token in list(zipped)[:10]],
            'time': endTimes[i]
        })
    
    with open('transcribe/transcripts/' + os.path.basename(transcriptFile) + '-tfidf-tokens.json', 'w') as f:
        json.dump(topTokens, f)
    
