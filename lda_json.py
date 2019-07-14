import nltk
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import stopwords
nltk.download('stopwords')

import gensim
from gensim import corpora, models
import pyLDAvis
import pyLDAvis.gensim

import json

def lda_json(transcriptFile, noTopics=10):
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
        if secCount > 30:
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
        processedSection = []
        for token in nltk.word_tokenize(section['transcript']):
            if token not in stopWords:
                processedSection.append(lemmatizer.lemmatize(token).lower())
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
    lda_model = gensim.models.LdaMulticore(corpus_tfidf, num_topics=noTopics, id2word=dictionary, passes=2, workers=2)
    print("model created")

    for idx, topic in lda_model.print_topics(-1):
        print('Topic: {} \nWords: {}'.format(idx, topic))

    document_topics_over_time = [[] for x in range(noTopics)]
    for i, val in enumerate(corpus_tfidf):
        print(str(int(sections[i]['time']) / 60) + " start min\n   ", end='')
        topics = lda_model.get_document_topics(val, minimum_probability=0.1)
        for topic in topics:
            document_topics_over_time[topic[0]].append(i)
    
    print(document_topics_over_time)


    visual = pyLDAvis.gensim.prepare(lda_model, corpus_tfidf, dictionary)
    pyLDAvis.save_html(visual, 'visual.html')
    #visualize(document_topics_over_time)
    return lda_model

def visualize(topics_t):
    import numpy as np
    import matplotlib.pyplot as plt

    topicLabels = ['Topic' + str(i) for i, x in range(noTopics)]

    ax.invert_yaxis()
    #ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())

    for idx, label in topicLabels:
        starts = topics_t[:, i]
        ax.barh(labels, 1, left=starts, height=0.5, label=colname, color=color)
        xcenters = starts + widths / 2

    fig, ax = plt.subplots(figsize=(9.2, 5))
    #labels = 
