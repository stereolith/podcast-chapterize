import nltk
from nltk.stem import WordNetLemmatizer, Cistem
from nltk.corpus import stopwords
from chapterize.mate_tools_lemma import MateToolsLemmazizer
nltk.download('wordnet')
nltk.download('stopwords')
def lemma(tokens, language):
    deLemmatizer = MateToolsLemmazizer()
    enLemmatizer = WordNetLemmatizer()
    deStemmer = Cistem()
    if language == 'en':
        return [enLemmatizer.lemmatize(token) for token in tokens]
    elif language == 'de':
        return deLemmatizer.lemmatize(tokens)

def remove_stopwords(tokens, language):
    """removes stopwords from a list of tokens 

    Args:
        tokens (list of strings): tokens to filter
        language (string): language (ISO 639-1 language code)
    """    
    nltk_stopword_languages = {
        'en': 'english',
        'de': 'german'
    }
    stopword_list = stopwords.words(nltk_stopword_languages[language])
    return list(filter(lambda t: t not in stopword_list, tokens))
