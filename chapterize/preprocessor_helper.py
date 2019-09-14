import nltk
from nltk.stem import WordNetLemmatizer, Cistem
nltk.download('wordnet')

enLemmatizer = WordNetLemmatizer()
deStemmer = Cistem()

def stem(token, language):
    if language == 'en':
        return enLemmatizer.lemmatize(token)
    elif language == 'de':
        return deStemmer.stem(token)