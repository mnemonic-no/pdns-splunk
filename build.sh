#!/bin/sh

version=$(grep -oP '(?<=version=).*' pdns/default/app.conf)
filename=dist/pdns-${version}.spl
mkdir -p dist
rm -f $filename

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
