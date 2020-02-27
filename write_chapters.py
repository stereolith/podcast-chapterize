from typing import List

# chapter object
class Chapter(object):
    def __init__(self, time = float, title = str):
        # chapter start time
        self.time = time

        # chapter title
        self.title = title

    def to_dict(self):
        return {
            'time': self.time,
            'title': self.title
        }

# Chapter writer class to handle writing chapter information
# to different files (i.e. audio files or text files)
# * main method write_chapters wirtes chapters to a file (i.e. text- or audio file)
# * should only accepts audio in suitable format 
class ChapterWriter(object):
    def write_chapters(self, format: str, chapters = List[Chapter], filepath = str):
        writer = _get_writer(format)
        return writer(chapters, filepath)

def _get_writer(format):
    if format == 'txt':
        return _write_to_txt
    elif format == 'mp3':
        return _write_to_mp3
    elif format == 'm4a':
        return _write_to_m4a
    else:
        raise ValueError(format)

def _write_to_mp3(chapters = List[Chapter], filepath = str):
    import eyed3
    from eyed3.id3 import Tag
    # write chapters to mp3 metadata
    tag = Tag()
    tag.parse(filepath)

    # remove chapters if already set
    # tag.table_of_contents.set(b'toc', child_ids=[])
    # for every chapter id (i.e. 'ch0' od. 'chp0'), do
    #   tag.chapters.remove(b'chp3')

    chapterIds = []
    for i, chapter in enumerate(chapters):
        endTime = int(chapter.time * 1000)
        startTime = 0
        if i != 0:
            startTime = int(chapters[i-1].time * 1000)
            
        chapterId = str.encode('ch' + str(i))
        newChapter = tag.chapters.set(chapterId, (startTime, endTime))
        newChapter.sub_frames.setTextFrame(b'TIT2', u'{}'.format(chapter.title))
        chapterIds.append(chapterId)
    
    tag.table_of_contents.set(b"toc", child_ids=chapterIds)
    tag.save()

def _write_to_txt(chapters = List[Chapter], filepath = str):
    from datetime import datetime
    # write chapters to text file
    with open(filepath, 'w') as f:
        out = ''
        for chapter in chapters:
            timeStr = datetime.utcfromtimestamp(chapter.time).strftime('%H:%M:%S.%f')[:-3]
            out += '{} {}\n'.format(timeStr, chapter.title)
        f.write(out)

def _write_to_m4a(chapters = List[Chapter], filepath = str):
    from datetime import datetime
    from subprocess import call
    from os import path
    import tempfile

    text_samples = ''
    for chapter in chapters:
        time_str = datetime.utcfromtimestamp(chapter.time).strftime('%H:%M:%S.%f')[:-3]
        text_samples += f'<TextSample sampleTime="{time_str}" sampleDescriptionIndex="1" xml:space="preserve">{chapter.title}</TextSample>'

    ttxt_template = (
        f'<?xml version="1.0" encoding="UTF-8" ?>'
        f'<!-- GPAC 3GPP Text Stream -->'
        f'<TextStream version="1.1">'
        f'    <TextStreamHeader width="0" height="0" layer="65535" translation_x="0" translation_y="0">'
        f'        <TextSampleDescription horizontalJustification="center" verticalJustification="bottom" backColor="1f 1f 1f 0" verticalText="no" fillTextRegion="no" continuousKaraoke="no" scroll="None">'
        f'            <FontTable>'
        f'                <FontTableEntry fontName="Sans-Serif" fontID="1"/>'
        f'            </FontTable>'
        f'            <TextBox top="0" left="0" bottom="0" right="0"/>'
        f'            <Style styles="Bold " fontID="1" fontSize="18" color="0 0 0 ff"/>'
        f'        </TextSampleDescription>'
        f'    </TextStreamHeader>'
        f'{text_samples}'
        f'</TextStream>'
    )

    project_path = path.dirname(path.realpath(__file__))
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ttxt') as tf:
        tf.write(ttxt_template)
        tf.flush()
        call(f'{project_path}/libs/MP4Box/MP4Box -chap {tf.name} {filepath}', shell=True)
        

