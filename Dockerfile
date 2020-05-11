FROM alpine:edge

WORKDIR /app

# install python, java and python package and lib build dependencies
RUN echo @testing http://nl.alpinelinux.org/alpine/edge/testing >> /etc/apk/repositories && \
apk update && \
apk add --no-cache python3 build-base py3-lxml py3-pip py3-scipy py3-numpy py3-scikit-learn@testing zlib-dev curl git openjdk8-jre

# add project files to container
ADD . .

# set env vars: point to prebuilt ffmpeg and mp4box libs
ENV FFMPEG_PATH libs/ffmpeg/ffmpeg
ENV MP4BOX_PATH libs/MP4Box/MP4Box

# compile MP4Box
WORKDIR /app/libs/MP4Box
RUN git clone https://github.com/gpac/gpac gpac_public
WORKDIR /app/libs/MP4Box/gpac_public
RUN ./configure --static-mp4box && make
RUN cp /app/libs/MP4Box/gpac_public/bin/gcc/MP4Box /app/libs/MP4Box/MP4Box && rm -rf /app/libs/MP4Box/gpac_public/
WORKDIR /app

# install python requirements
RUN pip3 install -r requirements-ka3.txt && pip3 install -U pytest

# remove build dependencies
RUN apk del build-base libxml2 zlib-dev

# download fasttext model
RUN python3 -c "import fasttext.util; fasttext.util.download_model('de')"

RUN mkdir input && output

# pytest:
#CMD ["pytest", "-s", "test_ka3_chapterize.py"]

ENTRYPOINT ["python3", "ka3_chapterize.py"]
