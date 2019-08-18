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

def hdp_json(transcriptFile, minSegmentLength=30):
    try:
        with open(transcriptFile, "r") as f:
            transcript = json.loads(f.read())
    except OSError:
        print("File not found")
        return

    # preprocess: 
    # combine segments minSegmentLength is not reached, lowercase, lemmatize, remove stopwords
    processed = []
    combinedSections = []
    lemmatizer = WordNetLemmatizer()
    stopWords = set(stopwords.words('english'))
    wordCount = 0
    processedSection = []
    for i, section in enumerate(transcript):
        for word in section:
            if word['word'] not in stopWords:
                processedSection.append(lemmatizer.lemmatize(word['word']).lower())
        if wordCount >= minSegmentLength:
            # combined section reached minSegmentLength
            processed.append(processedSection)
            processedSection = []
            wordCount = 0
        elif len(section) < minSegmentLength or wordCount != 0:
            # section or combined sections are too short
            wordCount += len(section)
            combinedSections.append(i)
        else:
            # individual section exceeds minSegmentLength
            processed.append(processedSection)
            processedSection = []

    # combine sections of transcript together due to minSegmentLength
    for i in sorted(combinedSections, reverse=True):
        transcript[i].append(transcript[i+1])
        del transcript[i+1]

    print(str(len(combinedSections)) + ' segments combined due to minSegmentLength')

    # create dictionary (occurance of words per section)
    dictionary = gensim.corpora.Dictionary(processed)
    dictionary.filter_extremes(no_below=2, no_above=0.5)
    print("dictionary generated")

    #create bag of words-corpus 
    bow_corpus = [dictionary.doc2bow(doc) for doc in processed]

    tfidf = models.TfidfModel(bow_corpus)
    corpus_tfidf = tfidf[bow_corpus]

    hdp_model = gensim.models.HdpModel(corpus_tfidf, dictionary)
    print("hdp model generated")

    pp.pprint(hdp_model.print_topics(num_topics=15, num_words=10))

    for i, val in enumerate(corpus_tfidf):
        print(str(round( (int(transcript[i][0]['startTime']) / 60),1)) + " start min\n   ", end='')
        print(sorted(hdp_model[val], reverse=True, key=lambda tup: tup[1]))
