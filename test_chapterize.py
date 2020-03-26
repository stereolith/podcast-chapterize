# pytest tests
import pytest
import shutil
import json

# test files: english episode, from Accidental Tech Podcast
transcript_test_file_path = "test_files/atp367.mp3_transcript.json" # atp 367
transcript_segmented_file_path = "test_files/atp367_chapters.json" # atp 367
preprocessed_documents_path = "test_files/preprocessed_docs.json" # atp 368

# test data fixtures
@pytest.fixture
def transcript_file_path(tmp_path):
    path = tmp_path.joinpath('transcript.json')
    shutil.copyfile(transcript_test_file_path, path)
    return path

@pytest.fixture
def transcript_json():
    with open(transcript_test_file_path, 'r') as f:
        j = json.load(f)
    return j

@pytest.fixture
def segmented_transcript():
    with open(transcript_segmented_file_path, 'r') as f:
        j = json.load(f)
    return j

@pytest.fixture
def preprocessed_documents():
    with open(preprocessed_documents_path, 'r') as f:
        j =  json.load(f)
    return j

# @pytest.fixture
# def segmented_trancript():

# deprecated with chapterize factory refactor
def test_cosine_similarity(transcript_json):
    from transcribe.SpeechToTextModules.SpeechToTextModule import TranscriptToken
    from chapterize.cosine_similarity import cosine_similarity
    tokens = [TranscriptToken.from_dict(token) for token in transcript_json['tokens']]

    concat_segments = cosine_similarity(tokens, transcript_json['boundaries'], language='en', visual=False)

    assert len(concat_segments) > 1


# def test_chapter_namer(segmented_transcript):

#     # tokens = transcript_json['']
#     assert segmented_transcript[0] == None

def test_document_vectorizer(preprocessed_documents):
    from chapterize.cosine_similarity import DocumentVectorizer
    from scipy import sparse

    methods = ['tfidf', 'ft_average']
    for method in methods:
        dv = DocumentVectorizer(method)
        document_vectors = dv.vectorize_docs(preprocessed_documents, language='en')

        assert isinstance(document_vectors, sparse.csr.csr_matrix), f"method {method}: document vectors should be of type csr_matrix"
        assert document_vectors.shape[0] == len(preprocessed_documents), f"method {method}: there should be as many document vectors as input documents"