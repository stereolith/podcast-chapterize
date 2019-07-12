import nltk
from nltk.stem import WordNetLemmatizer 

from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

import json

def k_cluster(transcriptFile, k=15):
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
        if secCount > 40:
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
    vectorizer = TfidfVectorizer(max_df=0.5, min_df=2, stop_words='english')
    X = vectorizer.fit_transform(processed)

    km = KMeans(n_clusters=k, init='k-means++', max_iter=100, n_init=1)
    km.fit(X)

    for i, label in enumerate(km.labels_.tolist()):
        print("Section from min {} assigned to cluster {}".format(str(round(int(sections[i]['time']) / 60, 2)), label))

    return km