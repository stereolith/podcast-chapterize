import nltk
from nltk.stem import WordNetLemmatizer 

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

import numpy as np
from scipy.signal import savgol_filter
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt

import json

def cosine_similarity(transcriptFile, minSegmentLength=30 , visual=True):
    try:
        with open(transcriptFile, "r") as f:
            transcript = json.loads(f.read())
    except OSError:
        print("File not found")
        return

    # generate list of section lengths & durations
    sectionTime = []
    for i, section in enumerate(transcript):
        if i+1 < len(transcript):
            sectionTime.append({
                'startTime': section[0]['startTime'],
                'duration': transcript[i+1][0]['startTime'] - section[0]['startTime']
            })
        else:
            sectionTime.append({
                'startTime': section[0]['startTime'],
                'duration': transcript[-1][-1]['startTime'] / len(transcript)
            })
    combinedSections = []

    # preprocess: 
    # lowercase, lemmatize, remove stopwords
    # if section has less words than minSegmentLength, section is combined with next sections until minSegmentLength is reached
    processed = []

    lemmatizer = WordNetLemmatizer()
    wordCount = 0
    processedSection = ''
    for i, section in enumerate(transcript):
        for word in section:
            processedSection += ' ' + lemmatizer.lemmatize(word['word']).lower()
        if wordCount >= minSegmentLength:
            # combined section reached minSegmentLength
            processed.append(processedSection)
            processedSection = ''
            wordCount = 0
        elif len(section) < minSegmentLength or wordCount != 0:
            # section or combined sections are too short
            wordCount += len(section)
            combinedSections.append(i)
        else:
            # individual section exceeds minSegmentLength
            processed.append(processedSection)
            processedSection = ''

    # remove elements of sectionTime list that are superflous because of combined sections
    for i in sorted(combinedSections, reverse=True):
        del sectionTime[i]

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
    cosine_similarities_smooth = savgol_filter(cosine_similarities, 11, 4)

    # calculate local minima
    minima = argrelextrema(cosine_similarities_smooth, np.less)
    print('local minima found at ', minima)
    
    if visual:
        visualize(cosine_similarities_smooth, cosine_similarities, minima, sectionTime)

    return [cosine_similarities_smooth, minima, sectionTime]

def visualize(cosine_similarities, cosine_similarities_raw, minima, sectionTimes): 
    endTimes = []
    for section in sectionTimes[:-1]:
        endTimes.append((section['startTime'] + section['duration']) / 60)

    minimaX = [np.array(endTimes)[minimum] for minimum in minima]
    minimaY = [cosine_similarities[minimum] for minimum in minima]

    fig, ax = plt.subplots(figsize=(13, 6))

    plt.plot(endTimes, cosine_similarities_raw, 'lightblue', label='cosine similarity', zorder=0)
    plt.plot(endTimes, cosine_similarities, marker='.', label='smoothed cosine similarity', zorder=1)
    plt.scatter(minimaX, minimaY, c='red', label='topic shift', zorder=2)
    ax.legend()
    plt.ylabel('cosine similarity')
    plt.xlabel('time in minutes')
    plt.show()

