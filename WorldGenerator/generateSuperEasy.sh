#!/bin/bash

rm -rf Problems
mkdir Problems

python3 WorldGenerator.py 1000 Easy_world_ 5 5 1

echo Finished generating worlds!
python WorldGenerator.py 1000 Intermediate_world_ 16 16 40

python3 WorldGenerator.py 100 Expert_world_ 16 30 99