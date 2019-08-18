import nltk
from nltk.stem import WordNetLemmatizer 

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

import numpy as np
import matplotlib.pyplot as plt

import json

def k_cluster(transcriptFile, k=15, visual=True, tfidf2D=False):
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

    # preprocess: 
    # lowercase, lemmatize, remove stopwords
    processed = []

    lemmatizer = WordNetLemmatizer()
    for section in transcript:
        processedSection = ''
        for word in section:
            processedSection += ' ' + lemmatizer.lemmatize(word['word']).lower()
        processed.append(processedSection)

    # create vectorizer, incl. removal of stopwords
    vectorizer = TfidfVectorizer(min_df=4, max_df=0.95, stop_words='english')
    X = vectorizer.fit_transform(processed)

    if tfidf2D:
        # reduce tfidf vector to 2 dimensions for optimizinf k with silhouette_score-function
        X = X.todense()
        from sklearn.decomposition import PCA
        pca = PCA(n_components=2).fit(X)
        X = pca.transform(X) 

    km = KMeans(n_clusters=k, init='k-means++', max_iter=300, n_init=1)
    cluster_labels = km.fit_predict(X)

    for i, label in enumerate(km.labels_.tolist()):
        print("Section from min {} assigned to cluster {}".format(str(round(int(transcript[i][0]['startTime']) / 60, 2)), label))
    
    if visual:
        visualize(km.labels_.tolist(), k, sectionTime)

    return [km, X, cluster_labels]

def visualize(labels, k, sectionTime):
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
        xranges = [((sectionTime[t]['startTime']/60), (sectionTime[t]['duration']/60)) for t in document_cluster_over_time[i]]
        ax.broken_barh(xranges, (i-0.3, .6), facecolors='tab:blue')

    ax.set_yticklabels(clusterLabels)
    ax.set_xlabel('Time in minutes')
    ax.set_title('Cluster allocation over time')
    ax.grid(True)
    plt.margins(0.02, 0.05)
    plt.show()

def optimize_k_elbow(transcriptFile):
    # optimize k with elbow plot    
    distortions = []
    for i in range(1, 15):
        km = k_cluster(transcriptFile, i, False)
        distortions.append(km[0].inertia_)

    plt.plot(range(1, 15), distortions, marker='o')
    plt.xlabel('k (Number of clusters)')
    plt.ylabel('Distortion')
    plt.show()

def optimize_k_silhouette(transcriptFile):
    # optimize k with silhouette score
    silhouette_avgs = []
    for i in range(2, 20):
        km = k_cluster(transcriptFile, i, False, tfidf2D=True)
        print(type(km[0]))
        silhouette_avg = silhouette_score(km[1], km[2])
        silhouette_avgs.append(silhouette_avg)
        print(str(i) + " clusters, silhouette_score: " + str(silhouette_avg))
    
    print(len(silhouette_avgs))

    plt.plot(range(2, 20), silhouette_avgs, marker='o')
    plt.xlabel('k (Number of clusters)')
    plt.ylabel('Silhouette averages')
    plt.show()

    
