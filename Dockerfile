FROM debian

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential python3 python3-dev curl git python3-pip python3 openjdk-11-jre
ADD . .

RUN pip3 install -r requirements.txt
RUN python3 -c "import fasttext.util; fasttext.util.download_model('de')"

# beispiel-command:
ENTRYPOINT ["python3", "ka3_chapterize.py"]

