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
    tag.parse(audioFile)

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
    # write chapters to text file
    with open(filepath, 'w') as f:
        out = ''
        for chapter in chapters:
            timeStr = time.strftime('%H:%M:%S', time.gmtime(chapter.time))
            out += '{} {}\n'.format(timeStr, chapter.title)
        f.write(out)

def _write_to_m4a():
    pass
