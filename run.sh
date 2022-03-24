#!/bin/bash

unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     /opt/Blender/Blend --background --python blender/exploreObj.py;;
    Darwin*)    /Applications/Blender.app/Contents/MacOS/Blender --background --python blender/exploreObj.py;;
    CYGWIN*)    machine=Cygwin;;
    MINGW*)     machine=MinGw;;
    *)          machine="UNKNOWN:${unameOut}"
esac
echo ${machine}
