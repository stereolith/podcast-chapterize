from textblob_de import TextBlobDE
import gensim
from gensim import corpora, models

try:
    with open("input.txt", "r") as f:
        input_text = f.read()
    with open("stopwords.txt", "r") as f:
        stopwords = f.read().splitlines()
except OSError:
    print("File not found")


def removeMeta(str):
    return str[str.find("]")+2:]

def getMeta(str):
    return str[1:str.find("]")+1]

def getMin(str):
    min = 0
    min += int(str[1:3]) * 60
    min += int(str[4:6])
    return min

input_text = input_text.splitlines()
print( removeMeta(input_text[12]) )

sections = []


currentIndex = 0
currentSectionA = ""
currentSectionB = ""
lastMin = 0
minCount = 0
i = 0

while i < len(input_text):
    minutes = getMin(input_text[i])
    if minutes > lastMin:
        minCount += minutes - lastMin
        if minCount % 4 == 0:
            sections.append(currentSectionA + " ")
            currentSectionA = ""
        elif minCount % 2 == 0:
            sections.append(currentSectionB + " ")
            currentSectionB = ""
    currentSectionA += removeMeta(input_text[i])
    currentSectionB += removeMeta(input_text[i])
    i += 1
    lastMin = minutes

processed = []

# lowercase, lemmatize, filter out stopwords
for section in sections:
    blob = TextBlobDE(section).words.lower().lemmatize()
    blob = [word for word in blob if word not in stopwords]
    processed.append(blob)

# create dictionary (occurance of words per section)
dictionary = gensim.corpora.Dictionary(processed)
dictionary.filter_extremes(no_below=5, no_above=0.5, keep_n=100000)
print("dictionary generated")

#create bag of words-corpus 
bow_corpus = [dictionary.doc2bow(doc) for doc in processed]

tfidf = models.TfidfModel(bow_corpus)
corpus_tfidf = tfidf[bow_corpus]

lda_model = gensim.models.LdaMulticore(bow_corpus, num_topics=10, id2word=dictionary, passes=2, workers=2)
for idx, topic in lda_model.print_topics(-1):
    print('Topic: {} \nWords: {}'.format(idx, topic))

minutes = 0
for section in bow_corpus:
    print(str(minutes) + " start min\n   ", end='')
    print(lda_model.get_document_topics(section))
    minutes += 2