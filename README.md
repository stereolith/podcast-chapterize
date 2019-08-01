# podcast-chapterize 

This project aims to automatically provide longform audio podcast episodes with chapter markers. This is achieved with statistical natrual language processing algorithms that try to subdivide transcribed podcast episodes into topically cohesive parts.

[work in progress]

## Journal

### 01.08.2019
* Add minimum segment length parameter to lda and hdp approaches

### 30.07.2019
* New approach: calculate lexical similarity via cosine similarity of adjacent text segments
  * cosine similarity score (dot product) is calculated for pairs of documents, based on tf-idf weighted term-document matrix
  * algorithm considers position of segments in text as well because only adjacent segments are compared for similarity, versus clustering and topic modeling approaches that see the documents in corpus not as a segmented parts of a consecutive whole, but as documents in no particular order
  * minSegmentLength attribute can be set to combine adjacent segments if the word count is below a threshold value to reduce the number of very short segments that are not useful/ representative in similarity analysis
  * plot for cosine similarity (y) for each segment shift, projected on the segment start/ end times (x):
  ![cosine similarity for pod save the queen](doc_files/cosine_similarity_podsaveamerica.png)
    * a high cosine means high similarity, so valleys in this plot signal low similarity -> topic shifts
    * here, valleys represent actual topic shifts, i.e. advertisement breaks at minute 61-63 and minute 39-43 and topic shift at minute 64
  * next steps: boundary indentification (find local minima in plot)
  * topic modeling after text segmentation to find topic terms?

### 21.07.2019
* For k_means clustering, optimize for k (number of clusters)
  * "elbow"-approach (optimize_k_elbow function)
    * can not find elbow, problem with tfidf vector?
  * [silhouette analysis](https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_silhouette_analysis.html) approach (optimize_k_silhouette function)
    * local maximums give values for k that work well, when there are multiple high silhouette score averages in the search range for k, choose the high point with the lowest k
    * example: [**Pod Save America** Episode "Racist Hall of Fame"](https://crooked.com/podcast/racist-hall-of-fame) 
      * plot of silhouette score averages for k in range (2, 20); at k=3 there is a local maximum
      ![silhouette score average for k](doc_files/silhouette_avgs_podsaveamerica.png)
      * cluster allocation over time for k=3
      ![cluster allocation over time for k=3](doc_files/kmeans_cluster_k3_podsaveamerica.png)
      * Actual topic changes occur at t≈22 and t≈64; advertisement breaks occur at minute 61-63 and minute 39-43, which is almost perfectly represented by cluster 2; **promising results!!**
      * for k_cluster function, parameter tfidf2D=True has to be set if number of topics is determined with silhouette analysis
      * Improvement: exclude segments with less than x tokens?

### 19.07.2019
* Exploration of different approaches to text segmentation, as topic modeling first approaches yielded not very usable results:
  * Using a neural network ([Attention-based Neural Text Segmentation](https://arxiv.org/pdf/1808.09935.pdf))
  * [Text segmentation of spoken meeting transcripts](https://link.springer.com/content/pdf/10.1007%2Fs10772-009-9048-2.pdf)
    * based on TextTiling algorithm with lexical chaining and refinment using cue phrases
    * specifically for transcripts of spoken multi-party conversation (text that is rarely eypository and has a "poor structure, spontaneous nature of communication and often argumentative nature as well as their infor-mal style" (p.1re))
    * refinment using cue phrases is difficult when trying to achieve wide-domain application for many different podcasts, this step can be skipped
* Add plot of cluster allocation over time for kmeans clustering approach
* Update transcribe/transcribe_google.py script to include utterance structure from google speech to text api in json transcript output (google speech api gives usable segmentation of longform audio into utterances or segments, useful for eliminating segmentation with an arbritarily chosen segment width for preprocessing)
  * adapted kmeans, LDA and HDP approach to accept new transcript format; **topic/ cluster over time plot needs adjustment because of variable segment lengths**

### 17.07.2019
* Add plot of topic distribution over time with matplotlib for lda approach (ToDo: add graph to hdp and k-means approach)
  ![topic distribution over time](doc_files/topicsovertime.png)
* For segmentaiton, the LDA approach yields not much useful results, as consecutive transcript segments often are not labeled with the same topic, so grouping segments together is difficult. Reasons for this could be:
  * the arbritary chosen segmentation (i.e. 30s segments) of the transcript produces very fuzzy segments that may or may not contain topic-related tokens and are in itself not contained entities
  * hyperparameters need to be tuned: segment width, number of topics, passes through data
    * could try out automated parameter tuning, maybe optimize no of topics with perplexity value (https://www.mathworks.com/help/textanalytics/ug/choose-number-of-topics-for-LDA-model.html)
  * **differnent approach: topic modeling after (k-means) clustering for labeling segments?**

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
