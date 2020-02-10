class TranscriptToken(object):
    def __init__(self, token, time):
        # word token
        self.token = token

        # time of occurence in audio in seconds
        self.time = time

    def to_dict(self):
        return {
            'token': self.token,
            'time': self.time
        }

# Speech to text module that takes an URL to an audio file and creates a list of transcriptTokens
class SpeechToTextModule(object):
    def __init__(self):
        pass

