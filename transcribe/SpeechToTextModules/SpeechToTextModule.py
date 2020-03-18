from typing import List, Tuple

class TranscriptToken(object):
    def __init__(self, token = str, time = float):
        # word token
        self.token = token

        # time of occurence in audio in seconds
        self.time = time

    @classmethod
    def from_dict(cls, token_dict):
        token = cls(token_dict['token'], float(token_dict['time']))
        return token

    def to_dict(self):
        return {
            'token': self.token,
            'time': self.time
        }

    def parse_dict(self, d):
        self.token = d['token']
        self.time = d['time']
        return self

# Speech to text module that takes an URL to an audio file and creates a list of transcriptTokens
class SpeechToTextModule(object):
    def __init__(self):
        pass

    # main transcribe function
    # * filepath: path to audio file to transcribe
    # * language: audio langage (ISO 639-1 language code)
    # @returns: tuple
    #   ( - tokens (list[TransctiptToken]): listtranscript with list of TranscriptToken objects 
    def transcribe(self, filepath: str, language: str) -> Tuple[List[TranscriptToken], List[int]]:
        tokens = []
        boundaries = []
        return tokens, boundaries

