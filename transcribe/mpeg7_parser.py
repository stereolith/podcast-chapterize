# parser for mpeg7 transcript files

from bs4 import BeautifulSoup
# requires lxml parser

# parses mpeg7 file
# returns (tuple):
# - list of TranscriptToken()
# - boundaries (list of indices of first token in 2..n segment), returns empty list if only one segment
def parse_mpeg7(filepath):
    try:
        with open(filepath, "rb") as f:
            transcript = BeautifulSoup(f, "lxml-xml")
    except OSError:
        print("File not found")
        return

    transcription_tokens = []
    boundaries = []

    # find all mpeg7:audioSegment elements
    for audio_segment in transcript.find('mpeg7:TemporalDecomposition').find_all('mpeg7:AudioSegment'):
        # filter out audioSegments without spoken word content
        descriptor = audio_segment.find('mpeg7:AudioDescriptor', attrs={'xsi:type': 'ifinder:SpokenContentType'}, recursive=False)
        if descriptor:
            transcription = audio_segment.find('ifinder:Transcription')
            if transcription:
                start_times, duration = parse_duration_matrix(transcription.find('ifinder:StartTimeDurationMatrix').string)

                tokens = parse_spoken_unit_vector(transcription.find('ifinder:SpokenUnitVector').string)
                if len(start_times) != len(tokens):
                    print('could not match StartTimeDurationMatrix with SpokenUnitVector')
                    return

                for i, start_time in enumerate(start_times):
                    transcription_tokens.append(TranscriptToken(tokens[i], start_time))

                boundaries.append(len(transcription_tokens))

    return transcription_tokens, boundaries[0:-1]


def parse_duration_matrix(str):
    values = str.split()
    if len(values) % 2 != 0:
        print('matrix does not have a dimensionality of 2')
        return
    start_time = []
    duration = []
    for i, val in enumerate(values):
        if i % 2 is 0:
            start_time.append(int(val) / 1000)
        else:
            duration.append(int(val) / 1000)
    return start_time, duration

def parse_spoken_unit_vector(str):
    return str.split()


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