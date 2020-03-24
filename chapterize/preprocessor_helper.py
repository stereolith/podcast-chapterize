import nltk
from nltk.stem import WordNetLemmatizer, Cistem
from chapterize.mate_tools_lemma import MateToolsLemmazizer
nltk.download('wordnet')
def lemma(tokens, language):
    deLemmatizer = MateToolsLemmazizer()
    enLemmatizer = WordNetLemmatizer()
    deStemmer = Cistem()
    if language == 'en':
        return [enLemmatizer.lemmatize(token) for token in tokens]
    elif language == 'de':
        return deLemmatizer.lemmatize(tokens)
