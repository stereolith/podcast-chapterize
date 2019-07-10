import nltk
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import stopwords
nltk.download('stopwords')
import gensim
from gensim import corpora, models
from gensim.models import HdpModel

import pprint
import json
pp = pprint.PrettyPrinter(indent=2)

def hdp_json(transcriptFile):
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
    dictionary.filter_extremes(no_below=5, no_above=0.3, keep_n=100000)
    print("dictionary generated")

    #create bag of words-corpus 
    bow_corpus = [dictionary.doc2bow(doc) for doc in processed]

    tfidf = models.TfidfModel(bow_corpus)
    corpus_tfidf = tfidf[bow_corpus]

    hdp_model = gensim.models.HdpModel(corpus_tfidf, dictionary)
    print("hdp model generated")

    pp.pprint(hdp_model.print_topics(num_topics=15, num_words=10))

    for i, val in enumerate(corpus_tfidf):
        print(str(round( (int(sections[i]['time']) / 60),1)) + " start min\n   ", end='')
        print(sorted(hdp_model[val], reverse=True, key=lambda tup: tup[1]))
