FROM alpine:edge

WORKDIR /app

# install python, java and python package dependencies
RUN echo @testing http://nl.alpinelinux.org/alpine/edge/testing >> /etc/apk/repositories && \
apk update && \
apk add --no-cache python3 build-base py3-lxml py3-pip py3-scipy py3-numpy py3-scikit-learn@testing curl git openjdk8-jre

# add project files to container
ADD . .

# set env vars: point to prebuilt ffmpeg and mp4box libs
ENV FFMPEG_PATH libs/ffmpeg/ffmpeg
ENV MP4BOX_PATH libs/MP4Box/MP4Box

# install python requirements
RUN pip3 install -r requirements-ka3.txt && pip3 install -U pytest

# remove build dependencies
RUN apk del build-base libxml2

# download fasttext model
RUN python3 -c "import fasttext.util; fasttext.util.download_model('de')"

# pytest:
CMD ["pytest", "-s", "test_ka3_chapterize.py"]

# beispiel-command:
#ENTRYPOINT ["python3", "ka3_chapterize.px"]
#CMD ["python3", "ka3_chapterize.py", "test_files/FOLK_E_00346_SE_01_A_01_DF_01_2020-03-19_11-10-11_result.xml", "."]

