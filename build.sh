#!/bin/sh

version=$(grep -oP '(?<=version=).*' mpdns/default/app.conf)
filename=dist/mpdns-${version}.spl
mkdir -p dist
rm -f $filename

# Update documentation from README.md
cat README.md | sed -e 's/\!\[.*\?\]\(.*\?\)//g' | pandoc -t plain | sed '/^$/N;/^\n$/D' > mpdns/README

# Exclude files that will make splunk-appinspect fail
tar zcf $filename \
    --exclude-vcs-ignores \
    --exclude=./build.sh \
    --exclude=mpdns/local \
    --exclude=mpdns/metadata/local.meta \
    --exclude=__pycache__ \
    --exclude=act/bin/lib/chardet/docs/Makefile \
    --exclude=.git \
    --exclude=\*.pyc \
    --exclude=.gitignore \
    --exclude=.gitmodules \
    mpdns

splunk-appinspect inspect $filename
