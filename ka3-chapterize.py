# chapterize CLI for KA³ services
from transcribe.mpeg7_parser import parse_mpeg7
from chapterize.cosine_similarity import cosine_similarity
from math import floor
import argparse
import os
import time

def main(transcript, output):
    if not os.path.exists(output):
        print('output path does not exist or no permission to open')
        return

    # parse mpeg7
    transcript_tokens, boundaries = parse_mpeg7(transcript)
    print('no of tokens: ', len(transcript_tokens))
    print('boundaries at ', boundaries)

    # calculate chapters
    window_width = min(floor(len(transcript_tokens) / 8), 200)
    print('window width: ', window_width)

    chapters = cosine_similarity(transcript_tokens, boundaries, windowWidth=window_width, language='de', visual=False)
    
    # write chapters to txt file
    folder = os.path.abspath(output)
    filename = os.path.splitext(os.path.basename(transcript))[0]
    with open('{}/{}_chapters.txt'.format(folder, filename), 'w') as f:
        out = ''
        for chapter in chapters:
            timeStr = time.strftime('%H:%M:%S', time.gmtime(chapter['time']))
            out += '{} {}\n'.format(timeStr, chapter['name'])
        f.write(out)
    
    print('\nfound the following chapters:\n', chapters)

# parse comand line arguments
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('transcript', type=str, help='MPEG7 transcript file')
    parser.add_argument('output', type=str, help='Output folder')

    args = parser.parse_args()

    main(args.transcript, args.output)



