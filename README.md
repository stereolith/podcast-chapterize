# podcast-chapterize 

This project aims to automatically provide longform audio podcast episodes with chapter markers. This is achieved with statistical natrual language processing algorithms that try to subdivide transcribed podcast episodes into topically cohesive parts.

[work in progress]

## Journal

### 14.07.2019
* Testing of [TextTiling](https://www.aclweb.org/anthology/J97-1003) algorithm:
    * The TextTiling algorithm is unsuitable for this problem because it needs the input to be structured into paragraphs, as the algorithm groups together paragraph units into multiparagraph sections that are topically coherent. Output of the text to speech api can not infer this text structure and is more comparable to a text stream.
    * In addition, 'TextTiling is geared towards expository text; that is, text that explicitly explains or teaches, as opposed to, say, literary texts, since expository text is better suited to the main target applications of information retrieval and summarization.' (Hearst 1997, 35)
    * Marti A. Hearst, Multi-Paragraph Segmentation of Expository Text. Proceedings of the 32nd Meeting of the Association for Computational Linguistics, Los Cruces, NM, June, 1994. 
* Added topic modeling visualization of LDA model with [pyLDAvis](https://github.com/bmabey/pyLDAvis) module, outputs html file visual.html
  ![pyLDAvis visualization](doc_files/pyLDAvis.png?raw=true "Optional Title")
* [WIP] matplotlib visualization of (lda) topic distribution over time in a (discontinuous) horizontal bar chart with **x: time**; **y: topic (categorical)**

### 12.07.2019

* for kmeans cluster switched to sklearn workflow (scikit learn, better docs and more accessible)
* improved approach 3 (kmeans clustering) with TF-IDF vectorizer:
  * with a section length of 30s, groups of clusters can be made out easily:
    (Podcast "Hello Internet", Episode #125)
    ```
    Section from min 0.67 assigned to cluster 11
    Section from min 1.37 assigned to cluster 10
    Section from min 2.05 assigned to cluster 10
    Section from min 2.73 assigned to cluster 10
    Section from min 3.4 assigned to cluster 10
    Section from min 4.07 assigned to cluster 7
    Section from min 4.75 assigned to cluster 7
    Section from min 5.42 assigned to cluster 7
    Section from min 6.12 assigned to cluster 7
    Section from min 6.8 assigned to cluster 7
    Section from min 7.47 assigned to cluster 7
    Section from min 8.15 assigned to cluster 7
    Section from min 8.82 assigned to cluster 1
    Section from min 9.5 assigned to cluster 11
    Section from min 10.17 assigned to cluster 2
    ```
* Similar to approach 1, the number of clusters needs to be determined beforehand. Making this approach work with many different podcasts and episode lengths could be difficult, maybe a variable number of clusters depending on the length of the podcast episode could be a solution.

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
