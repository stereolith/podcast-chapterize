def stem(token, language):
    import nltk
    from nltk.stem import WordNetLemmatizer, Cistem
    nltk.download('wordnet')

    enLemmatizer = WordNetLemmatizer()
    deStemmer = Cistem()
    if language == 'en':
        return enLemmatizer.lemmatize(token)
    elif language == 'de':
        return deStemmer.stem(token)
