# pytest tests
import pytest
import shutil
import json
import os
import subprocess

mpeg7_transcript_file_path = "test_files/FOLK_E_00346_SE_01_A_01_DF_01_2020-03-19_11-10-11_result.xml"
audio_file_path = "test_files/FOLK_E_00346_SE_01_A_01_DF_01.mp3"

# test data fixtures
@pytest.fixture
def mpeg7_transcript_tmp_path(tmp_path):
    path = tmp_path.joinpath('FOLK_E_00346_SE_01_A_01_DF_01_2020-03-19_11-10-11_result.xml')
    shutil.copyfile(mpeg7_transcript_file_path, path)
    return path

@pytest.fixture
def audio_tmp_path(tmp_path):
    path = tmp_path.joinpath('FOLK_E_00346_SE_01_A_01_DF_01.mp3')
    shutil.copyfile(audio_file_path, path)
    return path

def test_mate_tools(tmp_path):
    from subprocess import call

    out_path = tmp_path.joinpath('out_conll_09')
    call(f"java -Xmx2G -classpath chapterize/mate_tools/transition-1.30.jar is2.lemmatizer2.Lemmatizer -model chapterize/mate_tools/models/lemma-ger-3.6.model -test test_files/conll_09 -out {out_path} -uc", shell=True)
    with open(out_path, 'rb') as f:
        print(f)
        out = f.read().decode()

    assert len(out) > 10

# integration test: ka3 cli
def test_ka3_cli_transcript(mpeg7_transcript_tmp_path):
    import subprocess
    tmp_dir = os.path.dirname(mpeg7_transcript_tmp_path)
    subprocess.run(['python3', 'ka3_chapterize.py', mpeg7_transcript_file_path, tmp_dir])

    chapters_file_path = os.path.join(tmp_dir, os.path.splitext(os.path.basename(mpeg7_transcript_tmp_path))[0] + '_chapters.txt')
    with open(chapters_file_path) as f:
        chap_lines = f.readlines()
    
    assert len(chap_lines) > 2
    
def test_ka3_cli_transcript_audio(mpeg7_transcript_tmp_path, audio_tmp_path):
    tmp_dir = os.path.dirname(mpeg7_transcript_tmp_path)
    subprocess.run([
        'python3',
        'ka3_chapterize.py',
        '-a',
        audio_tmp_path,
        mpeg7_transcript_file_path,
        tmp_dir
    ])

    file_basename = os.path.splitext(os.path.basename(mpeg7_transcript_tmp_path))[0]

    output_chapters_file_path = os.path.join(tmp_dir, file_basename + '_chapters.txt')
    with open(output_chapters_file_path) as f:
        chap_lines = f.readlines()

    output_audio_file_path = os.path.join(tmp_dir, file_basename + '.m4a')
    
    assert len(chap_lines) > 2
    assert check_for_chapters_in_audio(output_audio_file_path)

def check_for_chapters_in_audio(audio_path):
    result = subprocess.run(['libs/ffmpeg/ffmpeg', '-i', audio_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stderr = result.stderr.decode('utf-8')

    print(stderr)
    if 'Chapter Images' in stderr or 'Chapter #' in stderr:
        return True
    
    return False