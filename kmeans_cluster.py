import nltk
from nltk.stem import WordNetLemmatizer 

from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

import numpy as np
import matplotlib.pyplot as plt

import json

def k_cluster(transcriptFile, k=15, windowSize=40):
    try:
        with open(transcriptFile, "r") as f:
            transcript = json.loads(f.read())
    except OSError:
        print("File not found")
        return

    # split transcript into 20 second long documents
    sections = []
    currentSection = ''  
    lastSec = 0
    secCount = 0

    for word in transcript:
        seconds = word['startTime']
        secCount += seconds - lastSec
        currentSection += word['word'] + ' '
        if secCount > windowSize:
            sections.append({'transcript': currentSection, 'time': seconds})
            secCount = 0
            currentSection= ''
        lastSec = seconds

    # preprocess: 
    # lowercase, lemmatize, remove stopwords
    processed = []

    lemmatizer = WordNetLemmatizer()
    for section in sections:
        processedSection = ''
        for token in nltk.word_tokenize(section['transcript']):
            processedSection += ' ' + lemmatizer.lemmatize(token).lower()
        processed.append(processedSection)

    # create vectorizer, incl. removal of stopwords
    vectorizer = TfidfVectorizer(max_df=0.5, min_df=3, stop_words='english')
    X = vectorizer.fit_transform(processed)

    km = KMeans(n_clusters=k, init='k-means++', max_iter=100, n_init=1)
    km.fit(X)

    for i, label in enumerate(km.labels_.tolist()):
        print("Section from min {} assigned to cluster {}".format(str(round(int(sections[i]['time']) / 60, 2)), label))
    
    visualize(km.labels_.tolist(), k, windowSize)

    return km

def visualize(labels, k, windowSize):
    document_cluster_over_time = [[] for x in range(k)]
    for i, label in enumerate(labels):
        document_cluster_over_time[label].append(i)

    print(document_cluster_over_time)

    fig, ax = plt.subplots()

    clusterLabels = ['Cluster ' + str(i) for i in range(len(document_cluster_over_time))]

    y_pos = np.arange(len(document_cluster_over_time))

    ax.set_yticks(y_pos)
    ax.invert_yaxis()
    for i in range(len(document_cluster_over_time)):
        xranges = [(t*(windowSize/60), (windowSize/60)) for t in document_cluster_over_time[i]]
        ax.broken_barh(xranges, (i-0.3, .6), facecolors='tab:blue')

    ax.set_yticklabels(clusterLabels)
    ax.set_xlabel('Time in minutes')
    ax.set_title('Cluster allocation over time')
    ax.grid(True)
    plt.margins(0.02, 0.05)
    plt.show()