import nltk
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.cluster import KMeansClusterer
from sklearn.feature_extraction.text import CountVectorizer

import json

def k_cluster(transcriptFile, k=10):
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
        if secCount > 20:
            sections.append({'transcript': currentSection, 'time': seconds})
            secCount = 0
            currentSection= ''
        lastSec = seconds

    # preprocess: 
    # lowercase, lemmatize, remove stopwords
    processed = []

    stopWords = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    for section in sections:
        processedSection = ''
        for token in nltk.word_tokenize(section['transcript']):
            if token not in stopWords:
                processedSection += ' ' + lemmatizer.lemmatize(token).lower()
        processed.append(processedSection)

    # one-hot vecorizer
    vectorizer = CountVectorizer(binary=True)
    freqs = vectorizer.fit_transform(processed)
    oneHot = [freq.toarray()[0] for freq in freqs]

    model = KMeansClusterer(k, distance=nltk.cluster.util.cosine_distance, avoid_empty_clusters=True)
    clusters = model.cluster(oneHot, assign_clusters=True)

    for idx, cluster in enumerate(clusters):
        print("Start time: {} assigned to cluster {}.".format( str(int(sections[idx]['time']) / 60)[:6], cluster))
            