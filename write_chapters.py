import eyed3
from eyed3.id3 import Tag
import os
import time


def write_chapters(chapters, audioFile):

    # write chapters to text file
    folder = os.path.dirname(audioFile)
    filename = os.path.splitext(os.path.basename(audioFile))[0]
    with open('{}/{}_chapters.txt'.format(folder, filename), 'w') as f:
        out = ''
        for chapter in chapters:
            timeStr = time.strftime('%H:%M:%S', time.gmtime(chapter[0]))
            out += '{} {}\n'.format(timeStr, chapter[1])
        f.write(out)

    tag = Tag()
    tag.parse(audioFile)

    print(tag)

    chapterIds = []
    for i, chapter in enumerate(chapters):
        endTime, title = chapter
        endTime = int(endTime * 1000)
        startTime = 0
        if i != 0:
            startTime = int(chapters[i-1][0] * 1000)
            
        chapterId = str.encode('ch' + str(i))
        newChapter = tag.chapters.set(chapterId, (startTime, endTime))
        newChapter.sub_frames.setTextFrame(b'TIT2', u'{}'.format(title))
        chapterIds.append(chapterId)
    
    tag.table_of_contents.set(b"toc", child_ids=chapterIds)
    tag.save()
