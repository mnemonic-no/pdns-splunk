#!/bin/sh

version=$(grep -oP '(?<=version=).*' pdns/default/app.conf)
filename=dist/pdns-${version}.spl
mkdir -p dist
rm -f $filename

# Update documentation from README.md
cat README.md | sed -e 's/\!\[.*\?\]\(.*\?\)//g' | pandoc -t plain | sed '/^$/N;/^\n$/D' > pdns/README

# Exclude files that will make splunk-appinspect fail
tar zcf $filename \
    --exclude-vcs-ignores \
    --exclude=./build.sh \
    --exclude=pdns/local \
    --exclude=pdns/metadata/local.meta \
    --exclude=__pycache__ \
    --exclude=act/bin/lib/chardet/docs/Makefile \
    --exclude=.git \
    --exclude=\*.pyc \
    --exclude=.gitignore \
    --exclude=.gitmodules \
    pdns

splunk-appinspect inspect $filename
