# chapterize CLI for KA³ services
from math import floor
import argparse
import os
from shutil import copyfileobj
import time
import subprocess

def main(transcript, output, audio):
    if not os.path.exists(output):
        print('output path does not exist or no permission to open')
        return
    if audio != None and not os.path.exists(audio):
        print('could not find audio file')
        return

    from transcribe.mpeg7_parser import parse_mpeg7
    from chapterize.cosine_similarity import cosine_similarity
    from write_chapters import ChapterWriter

    # parse mpeg7
    transcript_tokens, boundaries = parse_mpeg7(transcript)
    print('no of tokens: ', len(transcript_tokens))
    print('boundaries at ', boundaries)

    # calculate chapters
    window_width = min(floor(len(transcript_tokens) / 8), 200)
    print('window width: ', window_width)

    chapters = cosine_similarity(transcript_tokens, boundaries, windowWidth=window_width, language='de', visual=False)
    
    print('\nfound the following chapters:\n', [chapter.to_dict() for chapter in chapters])

    cw = ChapterWriter()
    filename = os.path.basename(transcript).split('.')[0]
    print('filename= ', filename)
    cw.write_chapters(
        'txt',
        chapters, 
        os.path.join(output, f'{filename}_chapters.txt')
    )

    if audio:
        suffix = os.path.splitext(audio)[1]
        
        audio_target_path = os.path.join(output, f'{filename}.m4a')

        # todo: properly handle audio which is already in the target format
        # if suffix == '.m4a':
        #     with open(audio, 'rb') as src, open(audio_target_path, 'wb') as dst:
        #         copyfileobj(src, dst)
        # else:
        subprocess.Popen(f'./libs/ffmpeg/ffmpeg -y -i {audio} -c:a aac -b:a 192k {audio_target_path}', shell=True).wait()

        cw.write_chapters('m4a', chapters, audio_target_path)

# parse comand line arguments
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('transcript', type=str, help='MPEG7 transcript file')
    parser.add_argument('output', type=str, help='Output folder')
    parser.add_argument('-a', '--audio', type=str, help='audio file to convert to m4a audio file with chapters')

    args = parser.parse_args()

    main(args.transcript, args.output, args.audio)



