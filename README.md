# podcast-chapterize 

This project aims to automatically provide longform audio podcast episodes with chapter markers. This is achieved with statistical natrual language processing algorithms that try to subdivide transcribed podcast episodes into topically cohesive parts.


## Journal

### until 12.07.2019

Created first running prototype with the following features:

* podcast feed parsing (transcribe/parse_rss.py)
  * parse rss/ atom feed
  * grab latest episode (or specify episode no)
  * grab relevant podcast episode audio file
* preprocess audio file (transcribe/transcribe_google.py)
  * convert audio to LINEAR16/ PCM encoded wav using ffmpeg
* transcribe audio file using google speech api (transcribe/transcribe_google.py)
  * upload file as blob to google cloud storage
  * run speech recognition on blob
  * postprocess transcript (create array with elements {token, time of occurrence}) 

Three different approaches were taken so far to prepare the automatic segmentation of the document:

1. topic modeling of segments: LDA (Latent Dirichlet Allocation) (lda_json.py)
  * preprocess:
    * segment transcript into 20 second chunks (consecutive segments, could sliding window approach with overlapping segments give better results?)
    * lowercase, lemmatize and remove stopwords (using nltk module)
    * create a dictionary and filter extremes
    * create bag of word (bow) corpus
    * create tf-idf corups from bow corpus
      * **using a bow corpus weighted with TF-IDF (Term Frequency–Inverse Document Frequency) gives less weight to non-topic-relevant stopword-like tokens (that have high occurrence in spoken word transcripts) compared to a simple frequency vector represtation of the document**
  * topic modeling
    * create lda model with params: num_topics=12, passes=2 (these hyperparameters need tuning), using gensim module
    * print topics + topic tokens 
    * print topic distribution for each 20s-segment

2. topic modeling of segments: HDP (Hierarchical Dirichlet Process) (hdp_json.py)
  * preprocess: see lda preprocessing
  * topic modeling
    * create hdp model
    * print topics + topic tokens 
    * print topic distribution for each 20s-segment

3. k-means clustering of segments (kmeans_cluster.py)
  * preprocess:
    * segment transcript into 20 second chunks (consecutive segments, could sliding window approach with overlapping segments give better results?)
    * lowercase, lemmatize and remove stopwords (using nltk module)
    * create bow corpus with one-hot vectorizing (using nltk module)
  * clustering
    * create k-means model with params: distance=nltk.cluster.util.cosine_distance
    * for each 20s segment print cluster allocation

#### First results

**Approach 1** gives first usable results, but adjusting parameters like the segment length and the lda model hyperparameters could improve the model. The need to specify the number of topics beforehand is a big caveat for the universal application of the method to differnet podcasts, that vary greatly in topic density and occurrence. One possible solution is to determine a mean topic occurrence per time unit and then make the number of topics depend on the length of the podcast episode.

**Approach 2**: The HDP model can infer the number of topics itself, which is a big advantage over LDA (approach 1). Still, results are not yet usable. Improvements in hyperparameters and text segmentation could help here too.

**Approach 3**: Results of clustering do not yet give usable results. Preprocessing could be improved (use TD-IDF with a cutoff weight to filter out non-relevant tokens before one-hot encoding?)
