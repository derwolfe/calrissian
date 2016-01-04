#!/bin/bash

set -x;
set -e;
mkdir -p wheelhouse;

docker build -t calrissian-base -f base.docker .;
docker build -t calrissian-builder -f build.docker .;
docker run --rm \
       -v "$(pwd)":/application -v "$(pwd)"/wheelhouse:/wheelhouse \
       calrissian-builder;
docker build -t calrissian-run -f run.docker .;
