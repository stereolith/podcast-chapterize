import nltk
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import stopwords
nltk.download('stopwords')

import gensim
from gensim import corpora, models
import pyLDAvis
import pyLDAvis.gensim

import numpy as np
import matplotlib.pyplot as plt

import json

def lda_json(transcriptFile, noTopics=10, windowSize=30):
    try:
        with open(transcriptFile, "r") as f:
            transcript = json.loads(f.read())
    except OSError:
        print("File not found")
        return

    # split transcript into 20 second long documents
    #sections = []
    #currentSection = ''  
    #lastSec = 0
    #secCount = 0

    #for word in transcript:
    #    seconds = word['startTime']
    #    secCount += seconds - lastSec
    #    currentSection += word['word'] + ' '
    #    if secCount > windowSize:
    #        sections.append({'transcript': currentSection, 'time': seconds})
    #        secCount = 0
    #        currentSection= ''
    #    lastSec = seconds

    # preprocess: 
    # lowercase, lemmatize, remove stopwords
    processed = []

    stopWords = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    for section in transcript:
        processedSection = []
        for word in section:
            if word['word'] not in stopWords:
                processedSection.append(lemmatizer.lemmatize(word['word']).lower())
        processed.append(processedSection)

    # create dictionary (occurance of words per section)
    dictionary = gensim.corpora.Dictionary(processed)
    dictionary.filter_extremes(no_below=2, no_above=0.5)
    print("dictionary generated")

    #create bag of words-corpus 
    bow_corpus = [dictionary.doc2bow(doc) for doc in processed]

    tfidf = models.TfidfModel(bow_corpus)
    corpus_tfidf = tfidf[bow_corpus]

    # create model
    lda_model = gensim.models.LdaMulticore(corpus_tfidf, num_topics=noTopics, id2word=dictionary, passes=3, workers=2)
    print("model created")

    for idx, topic in lda_model.print_topics(-1):
        print('Topic: {} \nWords: {}'.format(idx, topic))

    document_topics_over_time = [[] for x in range(noTopics)]
    for i, val in enumerate(corpus_tfidf):
        print(str(int(transcript[i][0]['startTime']) / 60) + " start min\n   ", end='')
        topics = lda_model.get_document_topics(val, minimum_probability=0.1)
        print(topics)
        for topic in topics:
            document_topics_over_time[topic[0]].append(i)

    visual = pyLDAvis.gensim.prepare(lda_model, corpus_tfidf, dictionary)
    pyLDAvis.save_html(visual, 'visual.html')
    #visualize(document_topics_over_time, windowSize)
    return lda_model

def visualize(topics_t, windowSize):
    fig, ax = plt.subplots()

    topicLabels = ['Topic ' + str(i) for i in range(len(topics_t))]

    y_pos = np.arange(len(topics_t))

    ax.set_yticks(y_pos)
    ax.invert_yaxis()
    for i in range(len(topics_t)):
        xranges = [(t*(windowSize/60), (windowSize/60)) for t in topics_t[i]]
        ax.broken_barh(xranges, (i-0.3, .6), facecolors='tab:blue')

    ax.set_yticklabels(topicLabels)
    ax.set_xlabel('Time in minutes')
    ax.set_title('Topic distribution over time')
    ax.grid(True)
    plt.margins(0.02, 0.05)
    plt.show()