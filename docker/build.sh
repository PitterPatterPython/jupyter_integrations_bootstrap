#!/bin/bash

set -e

PVER="python_312"
PY_VER="3.12.10-bookworm"

cwd=`pwd`

BASE_TAG="integrations_base_${PVER}"
FINAL_TAG="jupyter_integrations_${PVER}"

cp jupyter_integrations.cfg ./$PVER/
cp entrypoint.sh ./$PVER/
cp jupyter_integration_data_sources_template.env ./$PVER/
cd $PVER

WORK_DIR=`mktemp -d`
cleanup() {
  rm -rf "$WORK_DIR"
  echo "Deleted temp working directory: $WORK_DIR."
}

trap "exit 1" hup int pipe quit term
trap cleanup exit

# Fails with alias'd podman. Use symlink instead.
[[ "$(command -pv docker)" ]] || { echo "docker is not installed" 1>&2 ; exit 1; }

### I have no idea what this block does...
### Probably should do this in $WORK_DIR to be idempotent
#if [ ${MYDEV} -eq "1" ]; then
#    CURPWD=`pwd`
#    cd ..
#    cd ..
#    tar zcf /tmp/jup_int.tgz jupyter_integration_base
#    cd ${CURPWD}
#    mv /tmp/jup_int.tgz ./
#    tar zxf jup_int.tgz
#
#    echo "DEV VERSION"
#    MYJUPDOCK="${MYJUPDOCK}_dev"
#    echo "Jupyter Dockerfile: ${MYJUPDOCK}"
#else
#    echo "NON DEV"
#fi
###

echo "PVER: $PVER"
echo "BASE_TAG: $BASE_TAG"
echo "FINAL_TAG: $FINAL_TAG"

docker_build(){
    local TAG=$1
    local PY_VER=${2:-$PY_VER}
    local TARGET=${3:-""}


    docker build \
        --build-arg="PY_VER=$PY_VER" \
        -t ${TAG} .

    if [ $? -eq 0 ]; then
        echo "Successfully completed Docker build for $TAG"
    else
        echo "Build for $TAG failed - exiting"
        exit 1
    fi
}

docker_build ${FINAL_TAG}

if [ $? -eq 0 ]; then
    echo "Final Build Complete"
    cd $cwd
else
    echo "Final Build for $PVER failed - exiting"
    cd $cwd
    exit 1
fi
