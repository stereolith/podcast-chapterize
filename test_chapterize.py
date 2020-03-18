# pytest tests
import pytest
import shutil
import json

transcript_test_file_path = "test_files/atp367.mp3_transcript.json"
transcript_segmented_file_path = "test_files/atp367_chapters.json"

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

# @pytest.fixture
# def segmented_trancript():

# deprecated with chapterize factory refactor
def test_cosine_similarity(transcript_json):
    from transcribe.SpeechToTextModules.SpeechToTextModule import TranscriptToken
    from chapterize.cosine_similarity import cosine_similarity
    tokens = [TranscriptToken.from_dict(token) for token in transcript_json['tokens']]

    concat_segments = cosine_similarity(tokens, transcript_json['boundaries'], language='en', visual=False)

    assert len(concat_segments) > 1


def test_chapter_namer(segmented_transcript):
    # tokens = transcript_json['']
    assert segmented_transcript[0] == None