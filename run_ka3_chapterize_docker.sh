#!/bin/bash

absPath() {
    case $1 in
        /*) echo $1;;
        *) echo $PWD/$1;;
    esac
}

output="${@: -1}"

if [[ $# -eq 0 ]]; then
    echo not enough arguments
    exit 1
fi

if [[ $1 == "-a" ]]; then
    docker run -it \
        --mount type=bind,source="$(absPath $2)",target=/app/input/audio \
        --mount type=bind,source="$(absPath $3)",target=/app/input/transcript \
        --mount type=bind,source="$(absPath $output)"=/app/output \
        lmnch1113/ka3-chapterize-cli -a /app/input/audio /app/input/transcript /app/output
else
    docker run -it \
        --mount type=bind,source="$(absPath $1)",target=/app/input/transcript \
        --mount type=bind,source="$(absPath $output)",target=/app/output \
        lmnch1113/ka3-chapterize-cli /app/input/transcript /app/output
fi

