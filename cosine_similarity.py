import nltk
from nltk.stem import WordNetLemmatizer 

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
# Note that the tf-idf functionality in sklearn.feature_extraction.text can produce normalized vectors, in which case cosine_similarity is equivalent to linear_kernel, only slower.

import numpy as np
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
    
    if visual:
        visualize(cosine_similarities, sectionTime)

    return [cosine_similarities, sectionTime]

def visualize(cosine_similarities, sectionTimes): 
    endTimes = []
    for section in sectionTimes[:-1]:
        endTimes.append((section['startTime'] + section['duration']) / 60)

    plt.plot(endTimes, cosine_similarities, marker='.')
    plt.ylabel('cosine similarity')
    plt.xlabel('time in minutes')
    plt.show()

